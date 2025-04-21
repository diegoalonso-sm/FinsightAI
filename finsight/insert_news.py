import asyncio
from typing import List, Dict

import typer
import weaviate.classes as wvc

from finsight.chunker.chunker import TextChunker
from finsight.chunker.strategies.recursive import RecursiveSplitter
from finsight.crawler.crawler import YahooFinanceNewsExtractor
from finsight.retriever.agent.inserter import Inserter
from finsight.retriever.client.connection import WeaviateClientFactory
from finsight.retriever.client.interface import SchemaManager

# CLI application for managing financial news ingestion and storage
app = typer.Typer(help="FinsightAI CLI for managing financial news ingestion and storage.")


def extract_yahoo_finance_news(duration_seconds: int, scroll_interval: int, max_articles: int) -> List[Dict]:

    """Extract news articles from Yahoo Finance using the YahooFinanceNewsExtractor."""

    extractor = YahooFinanceNewsExtractor(
        duration_seconds=duration_seconds,
        scroll_interval=scroll_interval,
        max_articles=max_articles,
    )

    return asyncio.run(extractor.run())


def insert_chunks_into_weaviate(documents: List[Dict], collection_name: str = "NewsChunksExample") -> None:

    """Insert chunked documents into a Weaviate collection."""

    with WeaviateClientFactory.connect_to_local() as client:

        properties = [
            wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="full_article", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="url", data_type=wvc.config.DataType.TEXT, skip_vectorization=True),
            wvc.config.Property(name="date", data_type=wvc.config.DataType.TEXT),
        ]

        schema_manager = SchemaManager(client)
        schema_manager.create_collection(collection_name, properties)

        inserter = Inserter(client, collection_name)

        inserter.insert_documents(
            documents=documents,
            uuid_properties=["url"],
        )


@app.command("insert_news")
def insert_news_command(
    duration_seconds: int = typer.Option(2, help="Total seconds to scroll Yahoo Finance."),
    scroll_interval: int = typer.Option(1, help="Seconds between scrolls."),
    max_articles: int = typer.Option(100, help="Maximum number of articles to extract."),
    #chunk_size: int = typer.Option(800, help="Maximum chunk size for splitting articles."),
    #chunk_overlap: int = typer.Option(100, help="Overlap between chunks."),
    collection_name: str = typer.Option("NewsChunksExample", help="Weaviate collection name to store news chunks."),
):

    typer.echo("[INFO] Extracting news...")
    articles = extract_yahoo_finance_news(duration_seconds, scroll_interval, max_articles)
    typer.echo(f"[INFO] Extracted {len(articles)} articles.")

    typer.echo("[INFO] Inserting into Weaviate...")
    insert_chunks_into_weaviate(articles, collection_name)
    typer.echo("[INFO] Insertion complete.")


if __name__ == "__main__":
    app()
