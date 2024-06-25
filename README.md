# Multilspy-Java

## Introduction
This repository hosts a fork of Microsoft's `monitors4codegen`, with the multilspy contents isolated and some Java components improved. 

**Important Notice:**

> [!WARNING]  
> This is a **fork** of [Microsoft's monitors4codegen](https://github.com/microsoft/monitors4codegen).
> 
> **No endorsement and/or sponsorship by Microsoft** are implied.
> 
> **No warranty** is given for any functionality.

This fork primarily aids LLM research in a very specific niche and does not aim to support most use cases of the original repository. For the full version and comprehensive support, please refer to the original [monitors4codegen repository](https://github.com/microsoft/monitors4codegen).

## Repository Contents
1. [`multilspy`](#4-multilspy): A language server client, to easily obtain and use results of various static analyses provided by a large variety of language servers that communicate over the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/). `multilspy` is intended to be used as a library to easily query various language servers, without having to worry about setting up their configurations and implementing the client-side of language server protocol. `multilspy` currently supports running language servers for Java, Rust, C# and Python, and we aim to expand this list with the help of the community.


## `multilspy`
`multilspy` is a cross-platform library that we have built to set up and interact with various language servers in a unified and easy way. [Language servers]((https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/)) are tools that perform a variety of static analyses on source code and provide useful information such as type-directed code completion suggestions, symbol definition locations, symbol references, etc., over the [Language Server Protocol (LSP)](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/). `multilspy` intends to ease the process of using language servers, by abstracting the setting up of the language servers, performing language-specific configuration and handling communication with the server over the json-rpc based protocol, while exposing a simple interface to the user.

Since LSP is language-agnostic, `multilspy` can provide the results for static analyses of code in different languages over a common interface. `multilspy` is easily extensible to any language that has a Language Server and currently supports Java, Rust, C# and Python and we aim to support more language servers from the [list of language server implementations](https://microsoft.github.io/language-server-protocol/implementors/servers/).

Some of the analyses results that `multilspy` can provide are:
- Finding the definition of a function or a class ([textDocument/definition](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_definition))
- Finding the callers of a function or the instantiations of a class ([textDocument/references](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_references))
- Providing type-based dereference completions ([textDocument/completion](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_completion))
- Getting information displayed when hovering over symbols, like method signature ([textDocument/hover](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_hover))
- Getting list/tree of all symbols defined in a given file, along with symbol type like class, method, etc. ([textDocument/documentSymbol](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_documentSymbol))
- Please create an issue/PR to add any other LSP request not listed above

### Installation
To install `multilspy` using pip, execute the following command:
```
pip install https://github.com/LukvonStrom/multilspy-java/archive/main.zip
```

### Usage
Example usage:
```python
from monitors4codegen.multilspy import SyncLanguageServer
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger
...
config = MultilspyConfig.from_dict({"code_language": "java"}) # Also supports "python", "rust", "csharp"
logger = MultilspyLogger()
lsp = SyncLanguageServer.create(config, logger, "/abs/path/to/project/root/")
with lsp.start_server():
    result = lsp.request_definition(
        "relative/path/to/code_file.java", # Filename of location where request is being made
        163, # line number of symbol for which request is being made
        4 # column number of symbol for which request is being made
    )
    result2 = lsp.request_completions(
        ...
    )
    result3 = lsp.request_references(
        ...
    )
    result4 = lsp.request_document_symbols(
        ...
    )
    result5 = lsp.request_hover(
        ...
    )
    ...
```

`multilspy` also provides an asyncio based API which can be used in async contexts. Example usage (asyncio):
```python
from monitors4codegen.multilspy import LanguageServer
...
lsp = LanguageServer.create(...)
async with lsp.start_server():
    result = await lsp.request_definition(
        ...
    )
    ...
```

The file [src/monitors4codegen/multilspy/language_server.py](src/monitors4codegen/multilspy/language_server.py) provides the `multilspy` API. Several tests for `multilspy` present under [tests/multilspy/](tests/multilspy/) provide detailed usage examples for `multilspy`. The tests can be executed by running:
```bash
pytest tests/multilspy
```

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
