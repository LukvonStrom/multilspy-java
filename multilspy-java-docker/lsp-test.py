import asyncio
from contextlib import asynccontextmanager, contextmanager
import json
import os
import pathlib

from shutil import copyfile
from pathlib import Path, PurePath
import logging
import argparse
import time
from monitors4codegen.multilspy import LanguageServer
from monitors4codegen.multilspy.lsp_protocol_handler.lsp_requests import LspRequest
from monitors4codegen.multilspy.lsp_protocol_handler.lsp_types import Position
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger


loglevel = os.environ.get("LOGLEVEL", "DEBUG").upper()
logging.basicConfig(level=loglevel)

TIMEOUT_MINUTES = int(os.environ.get("TIMEOUT_MINS", 5))
BASE_OPERATION_DIR = Path("/mnt/repo")


def reregister_eventhandler(lsp: LanguageServer, event: str, callback: callable):
    lsp.server.on_notification(event, callback)
    lsp.server.on_notification_handlers[event] = callback


@asynccontextmanager
async def setup_lsp_server(completions_filepath: str):
    json_return = {"diagnostics": [], "error": None, "warnings": []}

    async def process_diagnostics(diag):
        irrelevant_strings = [
            "Build path specifies execution environment",
            "The compiler compliance specified is",
        ]
        if len(diag.get("diagnostics", [])) > 0:
            for d in diag.get("diagnostics", []):
                if any(
                    [
                        irrelevant_string in d.get("message", "")
                        for irrelevant_string in irrelevant_strings
                    ]
                ):
                    continue
                json_return["diagnostics"].append(d)

    class PartialFileLogger(MultilspyLogger):
        def log(
            self, debug_message: str, level: int, sanitized_error_message: str = ""
        ) -> None:
            """
            Log the debug and santized messages using the logger
            """
            debug_message = debug_message.replace("'", '"').replace("\n", " ")

            if level == 1:
                # or loglevel == "DEBUG":
                json_return["warnings"].append({"debug_message": debug_message})

            super().log(debug_message, level, sanitized_error_message)

    config = MultilspyConfig.from_dict(
        {"code_language": "java", "trace_lsp_communication": True}
    )
    logger = PartialFileLogger()
    lsp = LanguageServer.create(config, logger, BASE_OPERATION_DIR.as_posix())

    reregister_eventhandler(lsp, "textDocument/publishDiagnostics", process_diagnostics)

    print("Starting server...")

    # Using async context manager for starting the server
    async with lsp.start_server() as server:
        print("-" * 80)
        reregister_eventhandler(
            lsp, "textDocument/publishDiagnostics", process_diagnostics
        )
        with server.open_file(completions_filepath):
            yield (lsp, server, json_return)


async def main(filename: str) -> dict:
    try:

        # Using async context manager for starting the server
        completions_filepath = str(PurePath(filename))
        async with setup_lsp_server(completions_filepath) as magic_tuple:
            lsp, server, json_return = magic_tuple

            with open(completions_filepath, "r", encoding="utf-8") as cur_op_file:
                file_content = cur_op_file.read()
                lines = file_content.split("\n")

                # find line with . and get the line number
                tinker_line_indexes = [
                    i
                    for i, line in enumerate(lines)
                    if "(" in line and ")" in line and "//" not in line
                ]
                # print("tinker_line_indexes", tinker_line_indexes)

                tinker_lineno = tinker_line_indexes[0]
                tinker_line = lines[tinker_lineno]
                # get the col in the line of the dot and get the end of line
                # print("tinker_line", tinker_line)
                tinker_col = tinker_line.index("(")
                line_end_col = len(tinker_line) - 1
                remove_text = tinker_line[(tinker_col + 1) : line_end_col]

                # print("tinker_col", tinker_col, "line_end_col", line_end_col, "remove_text", remove_text)

            # tinker_line = 41
            deleted_text = server.delete_text_between_positions(
                completions_filepath,
                Position(line=tinker_lineno, character=tinker_col + 1),
                Position(line=tinker_lineno, character=line_end_col),
            )

            assert (
                deleted_text == remove_text
            ), "Deleted text does not match the expected text"

            # print("Deleted text:", deleted_text, remove_text)

            completions = await server.request_completions(
                completions_filepath,
                tinker_lineno,
                tinker_col + 1,
                allow_incomplete=True,
            )
            completions = [completion["completionText"] for completion in completions]

            server.insert_text_at_position(
                completions_filepath,
                line=tinker_lineno,
                column=tinker_col + 1,
                text_to_be_inserted=deleted_text,
            )
            await server.completions_available.wait()
            # for i in range(line_end_col):
            #     await lsp.request_hover(completions_filepath, tinker_lineno, i)

            open_file_buffer = lsp.open_file_buffers[
                pathlib.Path(
                    os.path.join(lsp.repository_root_path, completions_filepath)
                ).as_uri()
            ]

            textDocument = {"textDocument": {"uri": open_file_buffer.uri}}
            # await lsp.server.send.workspace_diagnostic({})
            # await lsp.server.send.text_document_diagnostic(params=textDocument)

            lsp.server.notify.will_save_text_document(params=textDocument)
            lsp.server.notify.did_save_text_document(params=textDocument)
            # await lsp.server.run_forever()
            await lsp.server.send.execute_command(
                {
                    "command": "java.project.refreshDiagnostics",
                    "arguments": [open_file_buffer.uri, "thisFile", False],
                }
            )
            await lsp.server.send.execute_command(
                {
                    "command": "java.project.refreshDiagnostics",
                    "arguments": [open_file_buffer.uri, "anyNonProjectFile", False],
                }
            )
            return json_return
    except Exception as e:
        json_return = {"diagnostics": [], "error": None, "warnings": []}
        print("-> -> -> Error occured", e)
        json_return["error"] = str(e)
        # print(json_return)
        return json_return


def restore_original_file(original_file_path: str, backup_file_path: str):
    copyfile(backup_file_path, original_file_path)


async def main_timeouted(filename: str):
    return await asyncio.wait_for(main(filename), timeout=TIMEOUT_MINUTES * 60)


if __name__ == "__main__":

    start_time = time.time()
    parser = argparse.ArgumentParser(description="Process a file.")
    parser.add_argument("-f", type=str, help="Path to the file")
    parser.add_argument(
        "-e",
        type=str,
        help="Whether there is an edit file in the mountable directory",
        required=False,
    )

    args = parser.parse_args()
    print("args:", args, flush=True)

    inspection_file = BASE_OPERATION_DIR / Path(args.f)
    print(f"Processing file: {inspection_file.absolute()}", flush=True)

    initial_status_file_content = asyncio.run(
        main_timeouted(inspection_file.absolute())
    )
    initial_data_path = os.getenv("INITIAL_DATA_PATH", "/tmp/status.json")
    print(f"Writing initial status to: {initial_data_path}", flush=True)

    print(f"Execution time: {time.time() - start_time} seconds", flush=True)

    start_time = time.time()

    initial_diag_count = len(initial_status_file_content["diagnostics"])
    with open(initial_data_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(initial_status_file_content, indent=4))

    if args.e and (args.e.lower() == "yes" or args.e.lower() == "y"):
        backup_file_path = f"{inspection_file}.backup"
        copyfile(inspection_file, backup_file_path)
        editpath = Path("/mnt/input") / inspection_file.name
        try:
            print(f"Checking for edit file at: {editpath}")
            if editpath.exists():
                copyfile(editpath, inspection_file)
                edit_status_file_content = asyncio.run(
                    main_timeouted(inspection_file.absolute())
                )

                edit_data_path = os.getenv("EDIT_DATA_PATH", "/tmp/edit_status.json")
                print(f"Writing edit status to: {edit_data_path}")

                edit_diag_count = len(edit_status_file_content["diagnostics"])

                print(
                    f"Initial file had {initial_diag_count} diagnostics, now we have {edit_diag_count} diagnostics"
                )

                with open(edit_data_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(edit_status_file_content, indent=4))
            else:
                raise FileNotFoundError(f"Edit file {editpath} not found")
        finally:
            restore_original_file(inspection_file, backup_file_path)
            os.remove(backup_file_path)
            print(f"2nd Execution time: {time.time() - start_time} seconds", flush=True)
