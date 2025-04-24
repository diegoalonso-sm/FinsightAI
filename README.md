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

## **Running the System**

### **Assistant (Interactive Chat)**

The Assistant is the core of **FinsightAI**, offering an interactive financial advisor experience.

To launch it:

```bash
python -m finsight.assistant
```

This will start a conversational session where you can:

- Ask financial-related questions,
- Retrieve the most relevant news from the vector database,
- Explore how news events could affect your investments.

> ⚡ **Note:**  
> The assistant is **currently under active development**.  
> For now, it can **only answer questions based on the financial news stored in the vector database (Weaviate)**.  
> In the future, **dynamic tool integration** (e.g., portfolio updates, automated reporting) will enable full investment advisory flows.

### **Feeder (Database Management CLI)**

The **Feeder** CLI is responsible for populating and managing the vector database with financial news articles.

To see the available commands:

```bash
python -m finsight.feeder --help
```

Available commands:

| Command             | Description                                                              |
|:--------------------|:-------------------------------------------------------------------------|
| `insert_news`        | Extract and insert news articles from Yahoo Finance into Weaviate.        |
| `show_news`          | Display stored news articles from a selected Weaviate collection.         |
| `create_schema`      | Create a new Weaviate collection with predefined properties.              |
| `delete_schema`      | Delete an existing Weaviate collection.                                   |
| `search_schema`      | Perform a semantic search over a Weaviate collection.                     |

### **Examples**

- **Insert financial news into Weaviate:**

```bash
python -m finsight.feeder insert_news --duration-seconds 2 --scroll-interval 1 --max-articles 50
```

- **Display inserted news articles:**

```bash
python -m finsight.feeder show_news --collection-name NewsChunksExample --max-articles 5
```

- **Delete an existing schema:**

```bash
python -m finsight.feeder delete_schema --collection-name FinancialArticles
```

- **Perform a semantic search:**

```bash
python -m finsight.feeder search_schema --collection-name NewsChunksExample --query "Tesla earnings" --max-documents 3
```

## Full Assistant Workflow + Example Conversation

### **Planned Tool and Action Flow**

| Actor                      | Message / Action                                                | What Happens Internally                                 | Tool involved |
|:---------------------------|:----------------------------------------------------------------|:--------------------------------------------------------|:--------------|
| **User**                   | "What relevant news is there today about AI?"                   | Starts a news search request.                           |               |
| **Agent**                  | Interprets the request.                                         | Decides that a search for news is needed.               |               |
| **Tool: search_news**      | Performs a `near_text` search in Weaviate using query = "AI".   | Retrieves relevant news articles.                       | `@agent.tool` |
| **Tool: summarize_news**   | Summarizes each retrieved article individually.                 | Uses the LLM to generate a short summary for each news. | `@agent.tool` |
| **Agent**                  | Displays the summarized articles to the user.                   | Presents the results concisely.                         |               |
| **User**                   | "How does this affect my investments in the AI & Robotics ETF?" | Requests impact analysis on portfolio.                  |               |
| **Agent**                  | Analyzes the impact based on summaries and portfolio context.   | Performs reasoning using the retrieved information.     |               |
| **Agent**                  | Provides the impact analysis response.                          | Shares a clear and thoughtful explanation.              |               |
| **User**                   | "What changes do you suggest?"                                  | Requests portfolio optimization recommendations.        |               |
| **Agent**                  | Proposes portfolio changes.                                     | Suggests reallocation based on news impact.             |               |
| **Agent**                  | Asks: "Would you like to apply these changes?"                  | Asks for user confirmation before taking any action.    |               |
| **User**                   | "Yes"                                                           | Approves the proposed portfolio changes.                |               |
| **Tool: update_portfolio** | Updates the portfolio in memory (non-persistent).               | Applies the approved changes to the `Portfolio` object. | `@agent.tool` |
| **User**                   | "Generate the final report."                                    | Requests a complete session summary.                    |               |
| **Tool: generate_report**  | Creates a detailed final report (news, analysis, decisions).    | Compiles and presents the full report.                  | `@agent.tool` |

### **Example of a full terminal conversation**

In this example, the user interacts with the assistant to analyze financial news and make portfolio adjustments.

```plaintext
User:
What relevant news is there today about AI?

Assistant:
I found the following relevant news:

1. Title: "NVIDIA launches new chips optimized for artificial intelligence"  
   URL: https://finance.example.com/nvidia-chips  
   Summary: NVIDIA introduced a new series of chips designed to accelerate AI applications, targeting sectors like robotics and healthcare.

2. Title: "OpenAI announces revolutionary AI model for enterprises"  
   URL: https://finance.example.com/openai-enterprise  
   Summary: OpenAI unveiled a new AI model specialized in enterprise solutions, aiming to boost productivity across multiple industries.

3. Title: "Boston Dynamics showcases advances in autonomous robots"  
   URL: https://finance.example.com/boston-robotics  
   Summary: Boston Dynamics demonstrated new robots capable of fully autonomous operation, potentially boosting industrial automation.

---

User:
How does this affect my investments in the AI & Robotics ETF?

Assistant:
These news articles are highly positive for the AI and robotics sector.  
Since the AI & Robotics ETF invests in companies like NVIDIA and Boston Dynamics, a favorable impact is expected, which could justify increasing its allocation in your portfolio.

---

User:
What changes do you suggest?

Assistant:
I suggest the following changes:

- AI & Robotics ETF: increase from 5% to 10%.
- Cash Reserve: reduce from 5% to 0% to fund the increase.

Would you like to apply these changes? (yes / no)

---

User:
Yes.

Assistant:
Changes successfully applied to your portfolio.

---

User:
Generate the final report.

Assistant:
Final Report:

Analyzed News:
- "NVIDIA launches new chips optimized for artificial intelligence"
- "OpenAI announces revolutionary AI model for enterprises"
- "Boston Dynamics showcases advances in autonomous robots"

Summaries:
- NVIDIA introduced a new series of AI chips.
- OpenAI launched a new AI model for businesses.
- Boston Dynamics advanced autonomous robotics.

Initial Portfolio:
- AI & Robotics ETF: 5%
- Cash Reserve: 5%

Final Portfolio:
- AI & Robotics ETF: 10%
- Cash Reserve: 0%

Justification for Changes:
- Increased AI & Robotics ETF allocation due to strong innovation and technological developments in the sector.

---

Thank you for using your financial assistant.
```

### **Tools involved in the flow**

- `@agent.tool search_news`: Retrieve relevant financial news from Weaviate.
- `@agent.tool summarize_news`: Summarize each retrieved news article individually.
- `@agent.tool update_portfolio`: Apply user-approved changes to the `Portfolio` (in memory).
- `@agent.tool generate_report`: Compile a full final report covering the entire session.
