# **FinsightAI - Chunker Module**

## **Overview**

The **Chunker** module provides a flexible and extensible system for **splitting text or documents into smaller pieces** ("chunks"), using different strategies optimized for various natural language processing tasks.

It enables recursive splitting, token-based splitting, or sentence-based splitting, making it ideal for preparing texts for semantic search, LLM embeddings, or information retrieval systems.

## **Structure**

The module is organized into several key components:

| File                      | Description                                                                                  |
|:--------------------------|:---------------------------------------------------------------------------------------------|
| `chunker.py`              | Main `TextChunker` class for chunking individual texts or batches of documents.              |
| `strategies/base.py`      | Abstract base class defining the `SplitterStrategy` interface.                               |
| `strategies/recursive.py` | Recursive splitting strategy based on paragraphs, sentences, spaces, and characters.         |
| `strategies/sentence.py`  | Sentence-level splitting strategy using NLTK's pretrained models.                            |
| `strategies/token.py`     | Token-based splitting strategy, useful for models with token limitations (e.g., GPT models). |

Each strategy is fully pluggable, enabling easy experimentation depending on the task requirements.

---

## **Requirements**

This module primarily depends on:

- [`langchain-text-splitters`](https://pypi.org/project/langchain-text-splitters/) – Advanced text splitting utilities.
- [`nltk`](https://www.nltk.org/) – Natural Language Toolkit for sentence tokenization.
- [`abc`](https://docs.python.org/3/library/abc.html) – Abstract base class functionality (for `SplitterStrategy`).
- [`typing`](https://docs.python.org/3/library/typing.html) – Type annotations.
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) (if needed in future extensions).

> Make sure that `langchain-text-splitters`, `nltk`, and related dependencies are installed before usage.

-  Additionally, **NLTK** requires downloading the `punkt` tokenizer model:

    ```python
    import nltk
    nltk.download('punkt')
    ```

## **Available Strategies**

| Strategy             | Description                                                                                           |
|:---------------------|:------------------------------------------------------------------------------------------------------|
| `RecursiveSplitter`  | Smartly splits based on structure: paragraphs ➔ sentences ➔ words ➔ characters.                      |
| `SentenceSplitter`   | Splits cleanly by sentences, ideal for fine-grained QA or dense retrieval systems.                    |
| `TokenSplitter`      | Splits based on token limits, essential for optimizing LLM input sizes and minimizing truncation.      |

All strategies implement the `SplitterStrategy` interface and can be swapped dynamically.

## **Execution Examples**

Each script (`*.py`) includes a `usage_example()` that can be run directly.

Some examples:

- **Recursive splitting example**

    ```bash
    uv run python -m finsight.chunker.strategies.recursive
    ```

- **Sentence-level splitting example**

    ```bash
    uv run python -m finsight.chunker.strategies.sentence
    ```

- **Token-based splitting example**

    ```bash
    uv run python -m finsight.chunker.strategies.token
    ```

- **Full pipeline example: Chunking multiple articles**

    ```bash
    uv run python -m finsight.chunker.chunker
    ```

## **Usage Example**

A typical flow:

```python
from finsight.chunker.chunker import TextChunker
from finsight.chunker.strategies.recursive import RecursiveSplitter

splitter = RecursiveSplitter(chunk_size=800, chunk_overlap=100)

chunker = TextChunker(splitter=splitter)

documents = [
    {"title": "Title 1", "content": "Long text 1..."},
    {"title": "Title 2", "content": "Long text 2..."}
]

chunked_documents = chunker.chunk_documents(documents, field="content")

for doc in chunked_documents:
    print(f"Document ID: {doc.get('id', 'N/A')}")
    print(f"Chunk Index: {doc['chunk_index']}")
    print(doc['chunk'])

```