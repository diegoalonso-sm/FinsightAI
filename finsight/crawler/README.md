# **FinsightAI - Crawler Module**

## **Overview**

This module provides the tools needed to **explore, extract, and structure financial news** from dynamic websites like Yahoo Finance.  
It uses `crawl4ai` to automatically navigate pages, sanitize collected links, and extract structured data through dynamically generated LLM-based schemas.

It is ideal for projects requiring news scraping, dataset generation for financial analysis, or semantic search systems.

## **Structure**

The module is organized into several components, each responsible for a specific part of the crawling and extraction workflow:

| File                    | Description                                                                                    |
|:------------------------|:-----------------------------------------------------------------------------------------------|
| `crawler.py`            | Main `NewsExtractor` class that coordinates URL exploration and structured content extraction. |
| `core/url/base`         | Defines exploration strategies like scrolling and deep search link extraction.                 |
| `core/content/base.py`  | Extracts structured content (JSON) from URLs using CSS or LLM-based strategies.                |
| `sanitizer/urls.py`     | Chains multiple URL sanitization filters to validate and normalize extracted links.            |  
| `sanitizer/datetime.py` | Cleans and formats datetime strings from extracted content.                                    |
| `schemas`               | Contains JSON schemas for extracting structured data.                                          |

## **Requirements**

This module primarily depends on:

- [`crawl4ai`](https://docs.crawl4ai.com/) – Asynchronous web crawling and structured content extraction.
- [`asyncio`](https://docs.python.org/3/library/asyncio.html) – Asynchronous programming framework in Python.
- [`abc`](https://docs.python.org/3/library/abc.html) – Abstract base classes.
- [`re`](https://docs.python.org/3/library/re.html) – Regular expressions for URL sanitization.
- [`json`](https://docs.python.org/3/library/json.html) – Serialization and deserialization of structured data.

> Make sure `crawl4ai` and other dependencies are installed and properly configured.

## **Execution Examples**

Each script contains a `usage_example()` that can be executed directly using:

- Demonstrates how to clean and filter a set of raw URLs.
    
    ```bash
    uv run python -m finsight.crawler.sanitizer.urls
    ```
  
- Demonstrates how to clean and format a datetime string.
    
    ```bash
    uv run python -m finsight.crawler.sanitizer.datetime
    ```

- Extracts structured information (title, date, full article) from a sample list of URLs.
    
    ```bash
    uv run python -m finsight.crawler.core.content.base
    ```
- Using a deep search strategy, it extracts valid internal links from a financial news page.
    
    ```bash
    uv run python -m finsight.crawler.core.url.deep_search
    ```

- Scrolls through a financial news page and extracts valid internal links.

    ```bash
    uv run python -m finsight.crawler.core.url.scroll_search
    ```

- Executes the full pipeline: explores Yahoo Finance news, filters article links, and extracts structured content using an LLM model.

    ```bash
    uv run python -m finsight.crawler.crawler
    ```

Each module includes a self-contained example demonstrating its usage with realistic parameters.
These examples show how to properly instantiate the components, configure expected inputs, and execute the functionality.
They are designed to serve as both quick tests and practical templates for real-world use cases.

