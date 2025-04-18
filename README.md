# **FinsightAI**

## **Project Structure**

The project is organized into several components, each responsible for a specific task in the overall workflow.
Below is a brief overview of each component's main responsibility:

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

## **Installation Guide**

This project is designed to run on Linux or WSL (Windows Subsystem for Linux), with an automated installation process
available for both. If you are using Windows only, manual installation is required.

It is heavily recommended to use WSL to ensure full compatibility and a smoother setup experience.

### **Linux / WSL**

To set up the `FinsightAI` project automatically, run the provided installation script:

```bash
sudo bash scripts/setup-linux.sh
```

A Python virtual environment will be created in the `.venv` directory, and all required [python](https://www.python.org/)
packages will be installed using [uv](https://docs.astral.sh/uv/) from Astral. Also, [Docker](https://docs.docker.com/)
will be installed if it is not already present on your system.

Another tool, [make](https://www.gnu.org/software/make/), will be installed. This will allow you to run common project
commands easily without needing to remember the exact command each time.

#### **Manual Installation**

If something goes wrong, check the terminal logs carefully to identify where the error occurred. Then, manually execute the commands inside `scripts/setup-linux.sh` one by one if needed.

#### **After installation**

Once the script completes:

1. Restart your terminal if you installed Docker for the first time (to refresh group permissions).
2. Activate the virtual environment manually:

    ```bash
    source .venv/bin/activate
    ```

3. Run the application:

    ```bash
    make run
    ```

4. Manage Docker services easily with:
    
    ```bash
    make up    # To start services
    make stop  # To stop services
    ```

### **Windows**

If you are using Windows without WSL, the installation process must be performed manually.

Follow these steps:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure Docker Engine is running.
2. Install [uv](https://astral.sh/uv/) by running the following command in PowerShell:

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. Install Python 3.12 if you don't have it already.

4. Open a PowerShell terminal and navigate to the project root directory.

5. Create the Python virtual environment and install dependencies:

   ```powershell
   uv install python=3.12
   uv venv .venv --prompt="FinsightAI" --python=python3.12
   uv sync
   uv run crawl4ai-setup
   ```

6. Build the required Docker images:

   ```powershell
   docker compose build
   ```

7. Activate the virtual environment manually:

   ```powershell
   .\.venv\Scripts\Activate
   ```

8. Start the application or manage services manually by referencing the commands in the `Makefile`.  
Since `make` is typically unavailable in native Windows environments, **you must manually run the equivalent commands** defined in the `Makefile` (for example: `python -m finsight` to run the app, `docker compose up -d ollama chroma` to start services).

You can open the `Makefile` to see the full list of available commands and their corresponding actions.