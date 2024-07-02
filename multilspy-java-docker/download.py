import asyncio
import os
import logging

from monitors4codegen.multilspy import LanguageServer
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG").upper())


async def main():
    print("Downloading Java Language Server", flush=True)
    config = MultilspyConfig.from_dict(
        {"code_language": "java", "trace_lsp_communication": True}
    )
    logger = MultilspyLogger()
    LanguageServer.create(config, logger, "/tmp/repo")
    print("Finished Downloading Java Language Server", flush=True)
    exit(0)


if __name__ == "__main__":
    asyncio.run(main())
