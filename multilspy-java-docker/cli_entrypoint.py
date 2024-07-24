import argparse
import asyncio
import json
import os
from pathlib import Path
from shutil import copyfile
import time
from java_lsp import main


BASE_OPERATION_DIR = Path(os.getenv("BASE_OPERATION_DIR", "/mnt/repo"))


async def main_timeouted(filename: str, timeout_mins: int):
    try:
        return await asyncio.wait_for(main(filename), timeout=timeout_mins * 60)
    except asyncio.TimeoutError:
        timeout_message = f"Language Server timeout of {timeout_mins} minutes reached"
        print("-" * 80, flush=True)
        print(timeout_message, flush=True)
        print("-" * 80, flush=True)
        return {"diagnostics": [], "error": timeout_message, "warnings": []}


def restore_original_file(original_file_path: str, backup_file_path: str):
    copyfile(backup_file_path, original_file_path)


def cli_entrypoint():

    start_time = time.time()
    parser = argparse.ArgumentParser(description="Process a file.")
    parser.add_argument("-f", type=str, help="Path to the file")
    parser.add_argument(
        "-e",
        type=str,
        help="Whether there is an edit file in the mountable directory",
        required=False,
    )
    parser.add_argument("-t", type=int, help="Timeout in minutes", required=False)

    args = parser.parse_args()
    print("args:", args, flush=True)


    timeout_minutes = 5

    inspection_file = BASE_OPERATION_DIR / Path(args.f)
    print(f"Processing file: {inspection_file.absolute()}", flush=True)

    backup_file_path = f"{inspection_file}.backup"
    copyfile(inspection_file, backup_file_path)

    initial_status_file_content = asyncio.get_event_loop().run_until_complete(
            main_timeouted(inspection_file.absolute(), timeout_minutes)
    )
    initial_data_path = os.getenv("INITIAL_DATA_PATH", "/tmp/status.json")
    print(f"Writing initial status to: {initial_data_path}", flush=True)

    print(f"Execution time: {time.time() - start_time} seconds", flush=True)

    start_time = time.time()

    initial_diag_count = len(initial_status_file_content["diagnostics"])
    with open(initial_data_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(initial_status_file_content, indent=4))

    initial_has_error = initial_status_file_content and initial_status_file_content.get("error", "") is not None and len(initial_status_file_content.get("error", "")) > 0

    if args.e and (args.e.lower() == "yes" or args.e.lower() == "y"):

        editpath = Path("/mnt/input") / inspection_file.name
        try:
            print(f"Checking for edit file at: {editpath}")
            if editpath.exists():
                copyfile(editpath, inspection_file)
                edit_status_file_content = asyncio.get_event_loop().run_until_complete(
                    main_timeouted(inspection_file.absolute(), timeout_minutes)
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
        if initial_has_error or edit_status_file_content and edit_status_file_content.get("error", "") is not None  and len(edit_status_file_content.get("error", "")) > 0:
            exit(1)
    elif initial_has_error:
        exit(1)


if __name__ == "__main__":
    cli_entrypoint()


# mvn test -B -Dorg.slf4j.simpleLogger.log.org.apache.maven.cli.event=info -Dorg.slf4j.simpleLogger.log.org.apache.maven.cli.transfer=error


# [DEBUG] incrementalBuildHelper#beforeRebuildExecution
# [INFO] Compiling
# [DEBUG] incrementalBuildHelper#afterRebuildExecution

# [INFO] -------------------------------------------------------------
# [ERROR] COMPILATION ERROR : 
# [INFO] -------------------------------------------------------------

# [INFO] -------------------------------------------------------
# [INFO]  T E S T S
# [INFO] -------------------------------------------------------

# [INFO] Results:
# [INFO] 
# [INFO] Tests run:


# [INFO] BUILD SUCCESS

# [INFO] BUILD FAILURE