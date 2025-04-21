import re
from abc import ABC, abstractmethod
from typing import List, Optional


class URLSanitizerHandler(ABC):

    """Abstract base class for URL sanitizers. Each sanitizer must implement the `sanitize` method to process and clean a given URL."""

    @abstractmethod
    def sanitize(self, url: Optional[str]) -> Optional[str]:
        pass


class RemoveQueryParametersSanitizer(URLSanitizerHandler):

    """
    Removes query parameters from a URL, preserving only the base path.

    Example:
    - Input: "https://example.com/page?param=value"
    - Output: "https://example.com/page"

    """

    def sanitize(self, url: Optional[str]) -> Optional[str]:

        """
        Remove any query parameters from the provided URL.

        :param url: The URL to sanitize.
        :type url: Optional[str]

        :return: The sanitized URL without query parameters, or None if input was None.
        :rtype: Optional[str]

        """

        if not url:
            return None

        return re.sub(r'\?.*$', '', url)


class PrefixSanitizer(URLSanitizerHandler):

    """Filters URLs that do not start with a specific prefix. Only URLs that start with the specified prefix are allowed."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    def sanitize(self, url: Optional[str]) -> Optional[str]:

        """
        Keep the URL only if it starts with the specified prefix.

        :param url: The URL to sanitize.
        :type url: Optional[str]

        :return: The URL if it matches the prefix, otherwise None.
        :rtype: Optional[str]

        """

        if not url:
            return None

        return url if url.startswith(self.prefix) else None


class RemoveNoneSanitizer(URLSanitizerHandler):

    """Ensures that only non-None URLs are kept. Useful for chain sanitization where intermediate steps may return None."""

    def sanitize(self, url: Optional[str]) -> Optional[str]:

        """
        Return the URL if it is not None.

        :param url: The URL to sanitize.
        :type url: Optional[str]

        :return: The same URL if not None, otherwise None.
        :rtype: Optional[str]

        """

        return url if url else None


class URLSanitizerChain:

    """Implements the chain of responsibility pattern for URL sanitization. Each sanitizer in the chain processes the URL in sequence."""

    def __init__(self, sanitizers: List[URLSanitizerHandler]):
        self.sanitizers = sanitizers

    def sanitize(self, urls: List[str], unique=False) -> List[str]:

        """
        Apply the sanitizers chain to a list of URLs.

        :param urls: List of raw URLs to sanitize.
        :type urls: List[str]

        :param unique: If True, removes duplicate URLs after sanitization.
        :type unique: bool

        :return: A list of sanitized URLs.
        :rtype: List[str]

        """

        cleaned_urls = []

        for url in urls:

            sanitized = self._sanitize_url(url)

            if sanitized is not None:
                cleaned_urls.append(sanitized)

        return cleaned_urls if unique else list(set(cleaned_urls))

    def _sanitize_url(self, url: str) -> Optional[str]:

        """
        Applies all sanitizers sequentially to a single URL.

        :param url: A single URL to sanitize.
        :type url: str

        :return: The fully sanitized URL, or None if any sanitizer discards it.
        :rtype: Optional[str]

        """

        for sanitizer in self.sanitizers:

            url = sanitizer.sanitize(url)

            if url is None:
                return None

        return url


def usage_example():

    """
    Demonstrates how to use URLSanitizerChain to clean a list of URLs.

    This example:
    - Creates a sanitizer chain with three sanitizers:
        - RemoveQueryParametersSanitizer: Removes query parameters from URLs.
        - PrefixSanitizer: Keeps only URLs starting with a specific prefix.
        - RemoveNoneSanitizer: Ensures no None values are kept.
    - Defines a list of raw URLs.
    - Applies the sanitizers to clean the URLs.
    - Prints the final list of sanitized, filtered URLs.

    Expected Output:
    [
        "https://finance.yahoo.com/news/stock-market-today.html",
        "https://finance.yahoo.com/news/another-news.html"
    ]

    """

    sanitizer_chain = URLSanitizerChain([
        RemoveQueryParametersSanitizer(),
        PrefixSanitizer("https://finance.yahoo.com/news/"),
        RemoveNoneSanitizer(),
    ])

    raw_links = [
        "https://finance.yahoo.com/news/stock-market-today.html?tsrc=fin-notif",
        "https://other.yahoo.com/sports/game.html?abc=123",
        "https://finance.yahoo.com/news/another-news.html?param=test",
        "https://finance.yahoo.com/news/stock-market-today.html",
    ]

    cleaned_links = sanitizer_chain.sanitize(raw_links)
    print(cleaned_links)


if __name__ == "__main__":
    usage_example()
