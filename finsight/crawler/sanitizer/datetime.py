import re
from abc import ABC, abstractmethod
from datetime import datetime

from finsight.models.client import LLMClient
from finsight.models.open_ai import OpenAIClient


class SanitizerStrategy(ABC):

    """Abstract base class for all sanitizer strategies."""

    @abstractmethod
    def sanitize(self, value: str) -> datetime:
        pass



class FullMonthDatetimeSanitizer(SanitizerStrategy):

    """Sanitizer strategy to convert date strings like 'Sat, April 19, 2025 at 3:18 PM GMT-4' into a 'YYYY-MM-DD' datetime object."""

    def sanitize(self, value: str) -> datetime:

        """
        Sanitize the input value and return a datetime object.

        :param value: The value to sanitize.
        :return: A datetime object.

        """

        value = re.sub(r"\sGMT[+-]?\d{1,4}", "", value)
        parsed_date = datetime.strptime(value.strip(), "%a, %B %d, %Y at %I:%M %p")
        return parsed_date


class AbbreviatedMonthDatetimeSanitizer(SanitizerStrategy):

    """Sanitizer strategy for date strings like 'Sun, Apr 20, 2025, 11:24 AM' into a 'YYYY-MM-DD' datetime object."""

    def sanitize(self, value: str) -> datetime:

        """
        Sanitize the input value and return a datetime object.

        :param value: The value to sanitize.
        :return: A date string formatted as 'YYYY-MM-DD'.

        """

        value = re.sub(r"\sGMT[+-]?\d{1,4}", "", value)
        parsed_date = datetime.strptime(value.strip(), "%a, %b %d, %Y, %I:%M %p")
        return parsed_date


class ChainedDatetimeSanitizer(SanitizerStrategy):

    """
    Composite sanitizer that tries multiple sanitizer strategies in sequence.

    This class implements the Strategy pattern by aggregating multiple
    SanitizerStrategy instances. It attempts to sanitize the input value
    by applying each strategy in order, returning the first successful result.

    If all strategies fail, it raises a ValueError with the last encountered exception.

    """

    def __init__(self, sanitizers: list[SanitizerStrategy]) -> None:

        """
        Initialize the CompositeSanitizer with a list of sanitizer strategies.

        :param sanitizers: List of sanitizer strategies to attempt.
        :type sanitizers: list[SanitizerStrategy]

        """

        self.sanitizers = sanitizers

    def sanitize(self, value: str) -> datetime:

        """
        Attempt to sanitize the input value using the available strategies.

        Tries each sanitizer strategy in order. Returns the first successful
        sanitized datetime object. If none succeed, raises a ValueError.

        :param value: The string value to sanitize.
        :type value: str

        :return: A datetime object representing the sanitized value.
        :rtype: datetime

        :raises ValueError: If no sanitizer could successfully process the input.

        """

        last_exception = None

        for sanitizer in self.sanitizers:

            try:
                return sanitizer.sanitize(value)

            except Exception as e:
                last_exception = e
                continue

        raise ValueError(f"No sanitizer could process the value: {value}") from last_exception


class LLMBasedDateSanitizer(SanitizerStrategy):

    """A sanitizer strategy that uses a language model to convert free-form date text into a datetime object. Supports formats with and without time."""

    def __init__(self, llm_client: LLMClient):

        """
        Initialize the LLMBasedDateSanitizer with a language model client.

        :param llm_client: An instance of a language model client.

        """

        self.llm_client = llm_client

    def sanitize(self, value: str) -> datetime:

        """
        Convert natural language date expressions to a datetime object.

        :param value: Input string containing the date/time in natural language.
        :return: Parsed datetime object (with time if available).
        :raises ValueError: If the LLM returns an invalid format.

        """

        system_prompt = (
            "You are a date formatter.\n"
            "If the input includes time, return it as: YYYY-MM-DD HH:MM:SS.\n"
            "If the input only includes a date, return it as: YYYY-MM-DD.\n"
            "Respond only with the formatted date string, no explanations."
        )

        user_prompt = f"Format this date: \"{value}\""

        response = self.llm_client.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(response.strip(), fmt)
            except ValueError:
                continue

        raise ValueError(f"Invalid date format returned by LLM: {response}")


def usage_example():

    """
    Example usage of the CompositeSanitizer class.

    This example:
    - Creates instances of individual sanitizers.
    - Creates a CompositeSanitizer with the list.
    - Sanitizes a date string into a datetime object.
    - Prints the datetime and formatted string.

    """

    sanitizer = ChainedDatetimeSanitizer([
        #FullMonthDatetimeSanitizer(),
        #AbbreviatedMonthDatetimeSanitizer(),
        LLMBasedDateSanitizer(
            OpenAIClient(
                model="gpt-3.5-turbo"
            )
        ),

    ])

    original_date = "Sat, April 19, 2025 at 9:30 AM GMT-4"
    sanitized_datetime = sanitizer.sanitize(original_date)

    print("Datetime object:", sanitized_datetime)
    print("Datetime type:", type(sanitized_datetime))


if __name__ == "__main__":
    usage_example()
