from monitors4codegen.multilspy import SyncLanguageServer
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger

config = MultilspyConfig.from_dict({"code_language": "java"}) 
logger = MultilspyLogger()
lsp = SyncLanguageServer.create(config, logger, "/abs/path/to/project/root/")
with lsp.start_server():
    result = lsp.request_definition(
        "relative/path/to/code_file.java", # Filename of location where request is being made
        163, # line number of symbol for which request is being made
        4 # column number of symbol for which request is being made
    )
    result2 = lsp.request_completions(
        
    )
    result3 = lsp.request_references(
        
    )
    result4 = lsp.request_document_symbols(
        
    )
    result5 = lsp.request_hover(
    )


# apk add python
# apk add py3-pip
# pip install https://github.com/LukvonStrom/monitors4codegen/archive/main.zip requests