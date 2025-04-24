from openai import OpenAI
from finsight.models.client import LLMClient

class OpenAIClient(LLMClient):

    """A client for interacting with OpenAI's new Responses API."""

    def __init__(self, api_key: str = None, model: str = 'gpt-3.5-turbo'):

        """
        Initialize the OpenAI client.

        :param api_key: OpenAI API key.
        :param model: OpenAI model identifier (e.g., 'gpt-4o', 'gpt-3.5-turbo').

        """

        from dotenv import load_dotenv

        load_dotenv()

        self.model = model
        self.client = OpenAI(api_key=api_key)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:

        """
        Generate a response using the OpenAI Responses API.

        :param system_prompt: Instructional context for the assistant.
        :param user_prompt: Actual user request.
        :return: The LLM-generated response.

        """

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )

        return response.output_text.strip()


def usage_example():

    """
    Example usage of the OpenAIClient class.

    This example:
    - Loads environment variables from a .env file.
    - Creates an OpenAI client.
    - Sets a system prompt for date formatting.
    - Sets a user prompt for a specific date.
    - Generates a response from the model.
    - Prints the ISO date returned by the model.

    """

    client = OpenAIClient(model="gpt-3.5-turbo")

    system_prompt = (
        "You are an assistant that returns dates in ISO format (YYYY-MM-DD) given natural language inputs."
        "You must return the date in ISO format only, without any additional text or explanation."
    )

    user_prompt = "Sat, April 19, 2025 at 9:30 AM GMT-4"

    try:
        result = client.generate_response(system_prompt, user_prompt)
        print(f"ISO date returned by model: {result}")

    except Exception as e:
        print(f"Error while generating response: {e}")


if __name__ == "__main__":
    usage_example()
