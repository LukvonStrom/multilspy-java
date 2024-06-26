import asyncio
import os
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
    lsp = LanguageServer.create(config, logger, ".")

    # Using async context manager for starting the server
    async with lsp.start_server() as server:
        print("Server started", flush=True)
        await lsp.server.shutdown()
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())
