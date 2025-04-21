import re
from abc import ABC, abstractmethod
from datetime import datetime


class SanitizerStrategy(ABC):

    """Abstract base class for all sanitizer strategies."""

    @abstractmethod
    def sanitize(self, value: str) -> datetime:
        pass


class DateFormatSanitizer(SanitizerStrategy):

    """Sanitizer strategy to convert date strings like 'Sat, April 19, 2025 at 3:18 PM GMT-4' into a datetime object."""

    def sanitize(self, value: str) -> datetime:

        """
        Sanitize the input value and return a datetime object.

        :param value: The value to sanitize.
        :return: A datetime object.

        """

        value = re.sub(r"GMT([+-])(\d)(?!\d)", r"GMT\g<1>0\g<2>00", value)
        parsed_date = datetime.strptime(value, "%a, %B %d, %Y at %I:%M %p GMT%z")

        return parsed_date


class DatetimeSanitizer(SanitizerStrategy):

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


def usage_example():

    """
    Example usage of the CompositeSanitizer class.

    This example:
    - Creates instances of individual sanitizers.
    - Creates a CompositeSanitizer with the list.
    - Sanitizes a date string into a datetime object.
    - Prints the datetime and formatted string.

    """

    sanitizer = DatetimeSanitizer([
        DateFormatSanitizer(),
    ])

    original_date = "Sat, April 19, 2025 at 9:30 AM GMT-4"
    sanitized_datetime = sanitizer.sanitize(original_date)

    print("Datetime object:", sanitized_datetime)
    print("Formatted:", sanitized_datetime.strftime("%Y-%m-%d %H:%M:%S%z"))


if __name__ == "__main__":
    usage_example()
