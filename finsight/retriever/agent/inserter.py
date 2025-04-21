from typing import List, Dict

import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5

from finsight.retriever.client.connection import WeaviateClientFactory
from finsight.retriever.client.interface import SchemaManager


class Inserter:

    """
    Inserter agent for adding documents or chunks into a Weaviate collection.

    This agent uses dynamic batching to optimize large-scale insertions,
    handles failed insertions, and stops the process if too many errors occur.

    """

    def __init__(self, client: weaviate.WeaviateClient, collection_name: str) -> None:

        """
        Initialize the Inserter.

        :param client: An active Weaviate client instance.
        :param collection_name: The name of the target collection to insert data into.

        """

        self.client = client
        self.collection = self.client.collections.get(collection_name)

    def insert_documents(self, documents: List[Dict], uuid_properties: List[str], max_errors: int = 10) -> None:

        """
        Insert a list of documents into the collection with dynamic batching.

        :param documents: List of document dictionaries to insert.
        :param uuid_properties: List of property keys used to generate UUIDs.
        :param max_errors: Maximum allowed errors before stopping.

        """

        with self.collection.batch.dynamic() as batch:

            for document in documents:

                self._validate_document_type(document)
                obj_uuid = self._generate_uuid(document, uuid_properties)

                batch.add_object(
                    properties=document,
                    uuid=obj_uuid,
                )

    @staticmethod
    def _validate_document_type(document: Dict) -> None:

        """Validate that the document is a dictionary."""

        if not isinstance(document, dict):
            raise ValueError(f"Unsupported data type for insertion: {type(document)}")

    @staticmethod
    def _generate_uuid(document: Dict, uuid_properties: List[str]) -> str:

        """Generate a UUID based on specified document properties."""

        keys_for_uuid = {prop: document[prop] for prop in uuid_properties}
        return generate_uuid5(keys_for_uuid)


def usage_example():

    with WeaviateClientFactory.connect_to_local() as client:

        collection_name = "NewsChunksExample"

        properties = [
            wvc.config.Property(
                name="title",
                data_type=wvc.config.DataType.TEXT
            ),
            wvc.config.Property(
                name="chunk",
                data_type=wvc.config.DataType.TEXT
            ),
            wvc.config.Property(
                name="chunk_index",
                data_type=wvc.config.DataType.INT
            ),
            wvc.config.Property(
                name="url",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="date",
                data_type=wvc.config.DataType.TEXT
            ),
        ]

        SchemaManager(client).create_collection(collection_name, properties)

        documents = [
            {
                "title": "AI in Finance",
                "chunk": "Machine learning is reshaping investment strategies.",
                "chunk_index": 0,
                "url": "https://finance.yahoo.com/ai-in-finance",
                "date": "2025-04-20 09:00:00"
            }
        ]

        chunk_inserter = Inserter(client, "NewsChunksExample")

        chunk_inserter.insert_documents(
            documents=documents,
            uuid_properties=["title", "chunk_index"]
        )

        collection = client.collections.get("NewsChunksExample")
        response = collection.query.fetch_objects(
            limit=2,
            include_vector=True,
        )

        for obj in response.objects:

            print(f"Vector: {obj.vector}")
            print(f"Document: {obj.properties}")


if __name__ == "__main__":
    usage_example()
