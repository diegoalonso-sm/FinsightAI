import os

import weaviate
from weaviate.classes.init import Auth


class WeaviateClientFactory:

    """Factory class to connect to a Weaviate instance, either locally or in the cloud."""

    def __init__(self, client: weaviate.WeaviateClient):
        self.client = client

    def __enter__(self) -> weaviate.WeaviateClient:
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.client.close()

    @staticmethod
    def connect_to_local() -> weaviate.WeaviateClient:

        """
        Connect to a locally hosted Weaviate instance.

        :return: Weaviate client instance connected locally.
        :rtype: weaviate.WeaviateClient

        """

        return weaviate.connect_to_local()

    @staticmethod
    def connect_to_cloud() -> weaviate.WeaviateClient:

        """
        Connect to a Weaviate Cloud instance using environment variables.

        Required environment variables:
        - WEAVIATE_URL
        - WEAVIATE_API_KEY
        - OPENAI_APIKEY (for OpenAI integration)

        :return: Weaviate client instance connected to the cloud.
        :rtype: weaviate.WeaviateClient

        """

        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        openai_api_key = os.getenv("OPENAI_APIKEY")

        if not all([weaviate_url, weaviate_api_key, openai_api_key]):
            raise ValueError("Missing one or more environment variables: WEAVIATE_URL, WEAVIATE_API_KEY, OPENAI_APIKEY")

        return weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=Auth.api_key(api_key=weaviate_api_key),
            headers={
                "X-OpenAI-Api-Key": openai_api_key,
            }
        )


def usage_example():

    # Local Connection (Docker)
    with WeaviateClientFactory.connect_to_local() as client:
        print(f"Client is Running Correctly? {"Yes" if client.is_ready() else "No"}")

    # Cloud Connection
    # with WeaviateClientFactory.connect_to_cloud() as client:
        # (f"Client is Running Correctly? {"Yes" if client.is_ready() else "No"}")


if __name__ == "__main__":
    usage_example()
