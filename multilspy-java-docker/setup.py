import asyncio
import os
import pathlib
import logging

from monitors4codegen.multilspy import LanguageServer
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG").upper())


async def main():
    config = MultilspyConfig.from_dict(
        {"code_language": "java", "trace_lsp_communication": True}
    )
    logger = MultilspyLogger()
    repo_path = pathlib.Path("/mnt/repo")
    lsp = LanguageServer.create(config, logger, repo_path.as_posix())

    # Using async context manager for starting the server
    async with lsp.start_server() as server:
        pom_path = repo_path / "pom.xml"
        try:
            with server.open_file(pom_path):
                open_file_buffer = lsp.open_file_buffers[pom_path.as_uri()]

                text_document = {"textDocument": {"uri": open_file_buffer.uri}}

                lsp.server.notify.will_save_text_document(params=text_document)
                lsp.server.notify.did_save_text_document(params=text_document)
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
        except Exception as e:
            print(e)
        print("Server started")


if __name__ == "__main__":
    asyncio.run(main())
