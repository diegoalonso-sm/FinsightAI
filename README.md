# **FinsightAI**

| Component                           | Main Responsibility                                                               |
|-------------------------------------|-----------------------------------------------------------------------------------|
| **Crawler**                         | Automatically discover financial news article URLs from selected websites.        |
| **Scraper**                         | Extract the full content (title, body, date) from each discovered news URL.       |
| **Preprocessor**                    | Clean and structure the raw article content for downstream processing.            |
| **Embedder**                        | Transform cleaned news articles into vector embeddings for semantic search.       |
| **Vector Store**                    | Store and manage embeddings for efficient retrieval based on similarity.          |
| **Retriever**                       | Search the vector database and retrieve relevant news articles for user queries.  |
| **Interface (CLI)**                 | Provide a command-line interface for user interaction with the agent.             |
| **Portfolio Manager**               | Manage the investment portfolio and propose reallocation strategies.              |
| **Executor (Tool Calling Manager)** | Apply suggested changes to the portfolio upon user confirmation.                  |
| **Reporter**                        | Generate a final report explaining portfolio adjustments and decision rationales. |
