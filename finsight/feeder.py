import asyncio
from enum import Enum
from typing import List, Dict

import typer
import weaviate.classes as wvc

from rich.console import Console
from rich.table import Table
from rich.text import Text


from finsight.crawler.crawler import YahooFinanceNewsExtractor
from finsight.retriever.agent.inserter import Inserter
from finsight.retriever.agent.searcher import Searcher
from finsight.retriever.client.connection import WeaviateClientFactory
from finsight.retriever.client.interface import SchemaManager

# CLI application for managing financial news ingestion and storage
app = typer.Typer(help="FinsightAI CLI for managing financial news ingestion and storage.")
console = Console()


def extract_yahoo_finance_news(duration_seconds: int, scroll_interval: int, max_articles: int) -> List[Dict]:

    """Extract news articles from Yahoo Finance using the YahooFinanceNewsExtractor."""

    extractor = YahooFinanceNewsExtractor(
        duration_seconds=duration_seconds,
        scroll_interval=scroll_interval,
        max_articles=max_articles,
    )

    return asyncio.run(extractor.run())


def insert_news_into_weaviate(documents: List[Dict], collection_name: str = "NewsExample") -> None:

    """Insert chunked documents into a Weaviate collection."""

    with WeaviateClientFactory.connect_to_local() as client:

        schema_manager = SchemaManager(client)

        schema_manager.create_collection(collection_name,
            properties=[
             wvc.config.Property(
                 name="title",
                 data_type=wvc.config.DataType.TEXT,
                 tokenization=wvc.config.Tokenization.WORD,
                 skip_vectorization=True,
             ),
             wvc.config.Property(
                 name="full_article",
                 data_type=wvc.config.DataType.TEXT,
                 tokenization=wvc.config.Tokenization.WORD,
                 skip_vectorization=False,
             ),
             wvc.config.Property(
                 name="summary",
                 data_type=wvc.config.DataType.TEXT,
                 skip_vectorization=True,
                 tokenization=wvc.config.Tokenization.WORD
             ),
             wvc.config.Property(
                 name="url",
                 data_type=wvc.config.DataType.TEXT,
                 skip_vectorization=True,
             ),
             wvc.config.Property(
                 name="date",
                 data_type=wvc.config.DataType.DATE,
                 skip_vectorization=True
             ),
            ],
            vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-large",
                vectorize_collection_name=False
            ),
            inverted_index_config = wvc.config.Configure.inverted_index(
                bm25_b=0.75,
                bm25_k1=1.2
            ),
            reranker_config=wvc.config.Configure.Reranker.transformers()
            )

        inserter = Inserter(client, collection_name)

        inserter.insert_documents(
            documents=documents,
            uuid_properties=["url"],
            summarize=True,
        )


class NewsExtractor(Enum):

    """Enum for different news extractors."""

    YAHOO_FINANCE = "yahoo_finance"
    # ANOTHER_EXTRACTOR = "another_extractor"

    @staticmethod
    def get_extractor(name: str):

        extractors = {
            "yahoo_finance": extract_yahoo_finance_news,
            # "other_extractor": other_extractor_function,
        }

        try:
            return extractors[name.lower()]

        except KeyError:
            raise typer.BadParameter(f"Extractor '{name}' not found. Available: {', '.join(extractors.keys())}")


@app.command("list_extractors")
def list_extractors_command():

    """List available news extractors."""

    extractors = [extractor.value for extractor in NewsExtractor]
    typer.echo("Available extractors:")
    for extractor in extractors:
        typer.echo(f"- {extractor}")


@app.command("insert_news")
def insert_news_command(
    extractor_name: str = typer.Option("yahoo_finance", help="Name of the news extractor."),
    duration_seconds: int = typer.Option(2, help="Total seconds to scroll Yahoo Finance."),
    scroll_interval: int = typer.Option(1, help="Seconds between scrolls."),
    max_articles: int = typer.Option(100, help="Maximum number of articles to extract."),
    #chunk_size: int = typer.Option(800, help="Maximum chunk size for splitting articles."),
    #chunk_overlap: int = typer.Option(100, help="Overlap between chunks."),
    collection_name: str = typer.Option("NewsExample", help="Weaviate collection name to store news chunks."),
):

    typer.echo(f"[INFO] Using '{extractor_name}' news extractor...")
    extractor_func = NewsExtractor.get_extractor(extractor_name)
    articles = extractor_func(duration_seconds, scroll_interval, max_articles)
    typer.echo(f"[INFO] Extracted {len(articles)} articles.")

    typer.echo("[INFO] Inserting into Weaviate...")
    insert_news_into_weaviate(articles, collection_name)
    typer.echo("[INFO] Insertion complete.")


@app.command("show_news")
def show_news_command(
    collection_name: str = typer.Option("NewsExample", help="Weaviate collection name to fetch news chunks."),
    max_characters: int = typer.Option(500, help="Maximum characters to display for each article."),
    max_articles: int = typer.Option(10, help="Maximum number of articles to display."),
):

    """Fetch and display news articles from a Weaviate collection in a formatted table."""

    with WeaviateClientFactory.connect_to_local() as client:
        collection = client.collections.get(collection_name)
        response = collection.query.fetch_objects(
            limit=max_articles,
            include_vector=True,
        )

        table = Table(title=f"News from '{collection_name}' collection", show_lines=True)

        table.add_column("UUID", width=38, overflow="fold", style="dim")
        table.add_column("Date", width=28, style="cyan")
        table.add_column("Title", width=40, style="bold", overflow="ellipsis")
        table.add_column("Article", width=60, style="dim", overflow="ellipsis")
        table.add_column("Summary", width=60, style="dim", overflow="ellipsis")

        for obj in response.objects:

            props = obj.properties
            uuid = str(obj.uuid)
            date = str(props.get("date", "N/A"))
            title = str(props.get("title", "—"))[:max_characters]
            article = str(props.get("full_article", "—"))[:max_characters]
            summary = str(props.get("summary", "—"))[:max_characters]

            table.add_row(
                uuid,
                date,
                Text(title, overflow="ellipsis"),
                Text(article, overflow="ellipsis"),
                Text(summary, overflow="ellipsis")
            )

        console.print(table)


@app.command("delete_schema")
def hard_delete_command(
    collection_name: str = typer.Option("Example", help="Weaviate collection name to delete."),
):

    """Delete a Weaviate collection."""

    with WeaviateClientFactory.connect_to_local() as client:

        schema_manager = SchemaManager(client)
        schema_manager.delete_collection(collection_name)
        print(f"[INFO] Collection '{collection_name}' deleted.")


@app.command("search_schema")
def search_schema_command(
    collection_name: str = typer.Option("Example", help="Weaviate collection name to search."),
    query: str = typer.Option("Technology", help="Search query string for documents."),
    max_documents: int = typer.Option(5, help="Maximum number of documents to retrieve."),
):

    """Search for documents in a Weaviate collection."""

    with WeaviateClientFactory.connect_to_local() as client:

        searcher = Searcher(client=client, collection_name=collection_name)
        results = searcher.search_documents(query, limit=max_documents)

        for r in results:
            print(r)


if __name__ == "__main__":
    app()
