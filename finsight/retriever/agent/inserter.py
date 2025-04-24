from typing import List, Dict

import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5

from finsight.models.open_ai import OpenAIClient
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

    def insert_documents(self, documents: List[Dict], uuid_properties: List[str], summarize=False) -> None:

        """
        Insert a list of documents into the collection with dynamic batching.

        :param documents: List of document dictionaries to insert.
        :param uuid_properties: List of property keys used to generate UUIDs.
        :param summarize: If True, summarize the documents before insertion.

        """

        with self.collection.batch.dynamic() as batch:

            for document in documents:

                self._validate_document_type(document)
                obj_uuid = self._generate_uuid(document, uuid_properties)

                if self._object_exists(obj_uuid):
                    print(f"[SKIP] Object with UUID {obj_uuid} already exists.")
                    continue

                document = self._summarize(document) if summarize else None

                batch.add_object(
                    properties=document,
                    uuid=obj_uuid,
                )

                print(f"Adding object with UUID: {obj_uuid}")

    def _object_exists(self, obj_uuid: str) -> bool:

        """
        Check if an object with the given UUID already exists in the collection.

        :param obj_uuid: UUID to check.
        :return: True if object exists, False otherwise.

        """

        try:
            obj = self.collection.query.fetch_object_by_id(obj_uuid)
            return obj is not None

        except Exception:
            return False

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

    @staticmethod
    def _summarize(document):

        client = OpenAIClient(model="gpt-4o")
        article = document.get("full_article", "")

        system_prompt = (
            "You are a financial analyst assistant. Your task is to analyze financial news articles and produce"
            "concise, neutral summaries. Each summary must be a single paragraph, clearly explaining the key event,"
            "its relevance to companies or industries involved, and any quantitative or strategic information that"
            "could assist in basic financial analysis. Avoid opinions, speculation, or irrelevant details."
            "Focus on clarity and usefulness for financial decision-making."
        )

        user_prompt = f"Summarize the following financial news article: {article}"

        try:
            result = client.generate_response(system_prompt, user_prompt)
            document["summary"] = result
            # print(f"Summary returned by model: {result}")

        except Exception as e:
            print(f"Error generating summary: {e}")

        return document


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
