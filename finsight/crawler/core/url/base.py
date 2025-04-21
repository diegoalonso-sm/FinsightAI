import asyncio
import time
from abc import ABC, abstractmethod
from typing import List, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from finsight.crawler.sanitizer.urls import (
    URLSanitizerChain,
    PrefixSanitizer,
    RemoveQueryParametersSanitizer,
    RemoveNoneSanitizer,
)


class ExplorationStrategy(ABC):

    """Abstract base class for exploration strategies. Defines the contract for any strategy that explores a web page and extracts links."""

    @abstractmethod
    async def explore(self, crawler: AsyncWebCrawler, url: str, session_id: str) -> List[str]:
        pass


class URLExtractorCrawler:

    """Crawler to extract and sanitize URLs from a web page using a defined exploration strategy."""

    def __init__(self, crawler: AsyncWebCrawler, strategy: ExplorationStrategy, run_config: Optional[CrawlerRunConfig] = None):

        """
        Initialize the URL extractor.

        :param crawler: The crawler used to interact with the page.
        :type crawler: AsyncWebCrawler

        :param strategy: The exploration strategy to use.
        :type strategy: ExplorationStrategy

        :param run_config: Optional configuration for page loading.
        :type run_config: Optional[CrawlerRunConfig]

        """

        self.crawler = crawler
        self.strategy = strategy
        self.run_config = run_config or CrawlerRunConfig(session_id="session")
        self.session_id = self.run_config.session_id

    async def extract(self, url: str, sanitizer: Optional[URLSanitizerChain] = URLSanitizerChain([])) -> List[str]:

        """
        Extract and sanitize links from a given URL.

        :param url: URL to start extraction from.
        :type url: str

        :param sanitizer: Sanitization chain to apply to extracted URLs.
        :type sanitizer: Optional[URLSanitizerChain]

        :return: List of sanitized URLs.
        :rtype: List[str]

        """

        await self._load_page(url)
        urls = await self.strategy.explore(self.crawler, url, self.session_id)
        cleaned_urls = sanitizer.sanitize(urls)

        return cleaned_urls

    async def _load_page(self, url: str) -> None:

        """
        Load the page using the crawler.

        :param url: URL of the page to load.
        :type url: str

        :return: None
        :rtype: None

        """

        await self.crawler.arun(url=url, config=self.run_config)


if __name__ == "__main__":
    pass
