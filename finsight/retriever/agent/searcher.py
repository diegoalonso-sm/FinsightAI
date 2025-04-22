from typing import List, Dict

import weaviate
import weaviate.classes as wvc

from finsight.retriever.client.connection import WeaviateClientFactory


class Searcher:

    """
    Searcher agent for retrieving documents or chunks from a Weaviate collection.

    This agent performs semantic search queries using vector search mechanisms.

    """

    def __init__(self, client: weaviate.WeaviateClient, collection_name: str) -> None:

        """
        Initialize the Searcher.

        :param client: An active Weaviate client instance.
        :param collection_name: The name of the collection to search into.

        """

        self.client = client
        self.collection = self.client.collections.get(collection_name)

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, str]]:

        """
        Perform a semantic search in the collection.

        :param query: The search query text.
        :param limit: Maximum number of documents to retrieve.
        :return: A list of dictionaries with document fields.

        """

        response = self.collection.query.near_text(
            query=query,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(distance=True),
        )

        results = []

        for obj in response.objects:

            props = obj.properties
            results.append(props)

        return results

    def validate_client(self) -> None:

        """Optional: Validate that the client connection is healthy."""

        if not self.client.is_ready():
            raise RuntimeError("Weaviate client connection is not ready.")


def usage_example():

    with WeaviateClientFactory.connect_to_local() as client:

        searcher = Searcher(client=client, collection_name="News")
        results = searcher.search_documents("What is AMD?", limit=2)

        for r in results:
            print(r)


if __name__ == "__main__":
    usage_example()
