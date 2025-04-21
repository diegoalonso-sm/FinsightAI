# **FinsightAI - Retriever Module**

## **Overview**

This module provides the tools needed to **interact, manage, and populate a Weaviate vector database** for financial news storage and retrieval.  
It allows creating collections, inserting documents or news chunks, and managing local or cloud connections to Weaviate easily and efficiently.

It is ideal for projects requiring embedding financial data, semantic search, or retrieval augmented generation (RAG) over news datasets.

## **Structure**

The module is organized into several components, each responsible for a specific part of the storage and retrieval workflow:

| File                   | Description                                                                             |
|:-----------------------|:----------------------------------------------------------------------------------------|
| `agent/inserter.py`    | Inserter agent that batches and inserts documents or chunks into a Weaviate collection. |
| `client/connection.py` | Handles local or cloud connections to a Weaviate instance using a context manager.      |
| `client/interface.py`  | Schema manager for creating, deleting, and listing Weaviate collections dynamically.    |

## **Requirements**

This module primarily depends on:

- [`weaviate-client`](https://weaviate.io/developers/weaviate/client-libraries/python) – Official Python client to interact with Weaviate instances.
- [`uuid`](https://docs.python.org/3/library/uuid.html) – To generate consistent UUIDs for document identification.
- [`os`](https://docs.python.org/3/library/os.html) – For handling environment variables during cloud connections.

> Make sure `weaviate-client` and other dependencies are installed and properly configured.

## **Execution Examples**

Each script contains a `usage_example()` that can be executed directly using:

- Demonstrates how to create a connection to a local Weaviate instance.

    ```bash
    uv run python -m finsight.retriever.client.connection
    ```

- Demonstrates how to create and delete a collection with a defined schema.

    ```bash
    uv run python -m finsight.retriever.client.interface
    ```

- Demonstrates how to insert a batch of documents or news chunks into a Weaviate collection.

    ```bash
    uv run python -m finsight.retriever.agent.inserter
    ```

Each module includes a self-contained example demonstrating its usage with realistic parameters.  
These examples show how to properly instantiate the components, configure expected inputs, and execute the functionality.
They are designed to serve as both quick tests and practical templates for real-world use cases.

> **Note**  
>
> The current classes are designed to follow the official Weaviate documentation examples, and aim for a minimal
> working setup. In future iterations, the system is planned to be optimized by introducing additional functionality
> for **monitoring** and **visualizing** the database state through a more **user-friendly interface**.  
>
> See the official guide for more details: [Weaviate Quickstart - Local Setup](https://weaviate.io/developers/weaviate/quickstart/local)