import warnings
from typing import List

import weaviate
import weaviate.classes as wvc

from finsight.retriever.client.connection import WeaviateClientFactory

warnings.filterwarnings(
    "ignore",
    message=r"Accessing the 'model_fields' attribute on the instance is deprecated",
    category=DeprecationWarning
)


class SchemaManager:

    """Manages collection schemas in a Weaviate instance. Provides methods to create, delete, check, and list collections."""

    def __init__(self, client: weaviate.WeaviateClient):

        """
        Initialize a SchemaManager.

        :param client: An instance of WeaviateClient already connected.
        :type client: weaviate.WeaviateClient

        """

        self.client = client

    def create_collection(self, name: str, properties: List[wvc.config.Property]) -> None:

        """
        Create a new collection with OpenAI vectorizer and optional generative config.

        :param name: The name of the collection to create.
        :type name: str

        :param properties: A list of Property objects defining the collection schema.
        :type properties: List[wvc.config.Property]

        """

        if self.client.collections.exists(name):
            print(f"Collection '{name}' already exists.")
            return

        self.client.collections.create(
            name=name,
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=properties,
        )

        print(f"Collection '{name}' created successfully.")

    def delete_collection(self, name: str) -> None:

        """
        Delete an existing collection.

        :param name: The name of the collection to delete.
        :type name: str

        """

        if not self.client.collections.exists(name):
            print(f"Collection '{name}' does not exist.")
            return

        self.client.collections.delete(name)
        print(f"Collection '{name}' deleted successfully.")

    def list_collections(self) -> list[str]:

        """
        List all collections in the Weaviate instance.

        :return: List of collection names.
        :rtype: List[str]

        """

        collections = self.client.collections.list_all(simple=True)
        return list(collections.keys())

    def collection_exists(self, name: str) -> bool:

        """
        Check if a collection exists.

        :param name: The name of the collection to check.
        :type name: str

        :return: True if exists, False otherwise.
        :rtype: bool

        """

        return self.client.collections.exists(name)


def usage_example():

    with WeaviateClientFactory.connect_to_local() as client:

        schema_manager = SchemaManager(client)

        collection_name = "ArticleChunks"

        properties = [
            wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="chunk", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="chunk_index", data_type=wvc.config.DataType.INT),
            wvc.config.Property(name="url", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="date", data_type=wvc.config.DataType.TEXT),
        ]

        schema_manager.create_collection(collection_name, properties)

        print("Available collections:", schema_manager.list_collections())

        exists = schema_manager.collection_exists(collection_name)
        print(f"Does '{collection_name}' exist?: {exists}")

        schema_manager.delete_collection(collection_name)
        print("Available collections after deletion:", schema_manager.list_collections())

        exists = schema_manager.collection_exists(collection_name)
        print(f"Does '{collection_name}' exist?: {exists}")


if __name__ == "__main__":
    usage_example()
