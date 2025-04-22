# **FinsightAI - Retriever Module**

## **Overview**

The Retriever module provides a complete toolkit to **manage, populate, and query a Weaviate vector database** focused on **financial news storage and semantic retrieval**.  
It enables the dynamic creation of collections, efficient document insertion, and powerful semantic search over indexed financial data.

This module is ideal for projects requiring **embeddings, semantic search**, or **retrieval-augmented generation (RAG)** based on financial datasets.

## **Structure**

The module is organized into several subcomponents, each responsible for a key part of the retrieval workflow:

| File                   | Description                                                                                    |
|:-----------------------|:-----------------------------------------------------------------------------------------------|
| `agent/inserter.py`    | Inserter agent for batching and inserting documents or news chunks into a Weaviate collection. |
| `agent/searcher.py`    | Searcher agent for performing semantic searches over a Weaviate collection.                    |
| `client/connection.py` | Factory to handle local or cloud Weaviate connections using context managers.                  |
| `client/interface.py`  | Schema manager for dynamically creating, deleting, and listing Weaviate collections.           |

## **Requirements**

The module primarily relies on the following packages:

- [`weaviate-client`](https://weaviate.io/developers/weaviate/client-libraries/python) – Official Python client to interact with Weaviate.
- [`uuid`](https://docs.python.org/3/library/uuid.html) – To generate consistent UUIDs based on document fields.
- [`os`](https://docs.python.org/3/library/os.html) – To handle environment variables for cloud connectivity.

> Ensure `weaviate-client` is installed and properly configured before usage.

## **Usage Examples**

Each script includes a `usage_example()` function that can be executed directly to demonstrate typical workflows.

### **Connecting to Weaviate (Local or Cloud)**

```bash
uv run python -m finsight.retriever.client.connection
```

Establishes a connection to a locally running or cloud-hosted Weaviate instance.

---

### **Managing Collections**

```bash
uv run python -m finsight.retriever.client.interface
```

Demonstrates how to create, list, and delete collections with defined schemas dynamically.

---

### **Inserting Documents or News Chunks**

```bash
uv run python -m finsight.retriever.agent.inserter
```

Shows how to batch-insert documents into a collection with UUID generation based on selected fields.

---

### **Performing Semantic Search Queries**

```bash
uv run python -m finsight.retriever.agent.searcher
```

Executes a semantic search over documents using hybrid vector search strategies.

---

Each module includes self-contained examples demonstrating:

- How to instantiate the respective components,
- How to configure input parameters,
- How to execute the intended functionality.

These examples serve as **both functional tests** and **templates** for real-world integration.

## **Notes and Future Improvements**

- Current classes follow a minimal and practical setup aligned with the [official Weaviate examples](https://weaviate.io/developers/weaviate/quickstart/local).
- Future iterations are planned to include **error monitoring**, **insertion analytics**, and a **web-based interface** for improved visibility into the Weaviate database state.
