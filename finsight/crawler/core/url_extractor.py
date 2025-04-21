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


class ScrollExplorationStrategy(ExplorationStrategy):

    """Exploration strategy that scrolls the page and extracts internal links over time."""

    def __init__(self, duration_seconds: int = 10, scroll_interval: float = 1.0):

        """
        Initialize the scroll exploration strategy.

        :param duration_seconds: Total duration to scroll the page in seconds.
        :type duration_seconds: int

        :param scroll_interval: Interval between scrolls in seconds.
        :type scroll_interval: float

        """

        self.duration_seconds = duration_seconds
        self.scroll_interval = scroll_interval

    async def explore(self, crawler: AsyncWebCrawler, url: str, session_id: str) -> List[str]:

        """
        Explore the page and extract a list of URLs.

        :param crawler: The crawler instance to interact with the page.
        :type crawler: AsyncWebCrawler

        :param url: The URL of the page to explore.
        :type url: str

        :param session_id: Identifier for the browser session.
        :type session_id: str

        :return: List of extracted URLs.
        :rtype: List[str]

        """

        start_time = time.time()
        collected_links = []
        scroll_count = 0

        while (time.time() - start_time) < self.duration_seconds:

            result = await self._scroll_page(crawler, url, session_id)

            if not self._is_successful_result(result):
                scroll_count = await self._post_scroll_wait(scroll_count)
                continue

            extracted_links = self._extract_valid_internal_links(result)
            collected_links.extend(extracted_links)

            scroll_count = await self._post_scroll_wait(scroll_count)

        return collected_links

    async def _scroll_page(self, crawler: AsyncWebCrawler, url: str, session_id: str):

        """
        Perform a scroll action on the page.

        :param crawler: The crawler instance.
        :type crawler: AsyncWebCrawler

        :param url: The URL of the page.
        :type url: str

        :param session_id: Session identifier.
        :type session_id: str

        :return: The crawl result.

        """

        config = self._create_scroll_config(session_id)
        return await crawler.arun(url=url, config=config)

    @staticmethod
    def _create_scroll_config(session_id: str) -> CrawlerRunConfig:

        """
        Create a scroll-specific crawler configuration.

        :param session_id: Session identifier.
        :type session_id: str

        :return: Configuration for scrolling action.
        :rtype: CrawlerRunConfig

        """

        return CrawlerRunConfig(
            session_id=session_id,
            js_code="window.scrollTo(0, document.body.scrollHeight);",
            js_only=True,
            cache_mode=CacheMode.BYPASS,
        )

    @staticmethod
    def _is_successful_result(result) -> bool:

        """
        Check if the crawl result indicates a successful operation.

        :param result: The crawl result.
        :return: True if successful, False otherwise.
        :rtype: bool

        """

        return result is not None and result.success

    @staticmethod
    def _extract_valid_internal_links(result) -> List[str]:

        """
        Extract valid internal links from the crawl result.

        :param result: The crawl result.
        :return: List of href strings for valid links.
        :rtype: List[str]

        """

        links = result.links.get("internal", [])
        return [link["href"] for link in links if link.get("href")]

    async def _post_scroll_wait(self, scroll_count: int) -> int:

        """
        Wait for a specified interval after a scroll.

        :param scroll_count: The current number of scrolls performed.
        :type scroll_count: int

        :return: Updated scroll count after waiting.
        :rtype: int

        """

        await asyncio.sleep(self.scroll_interval)
        return scroll_count + 1


async def usage_example() -> None:

    """
    Example usage of the URLExtractorCrawler with ScrollExplorationStrategy.

    This example demonstrates:
    - Configuring the browser to run in visible (non-headless) mode with lightweight page loading.
    - Setting up a crawler to scroll a financial news page and extract internal links.
    - Applying a sanitizer chain to:
      - Remove query parameters from URLs.
      - Keep only links starting with a specific prefix.
      - Discard None values.
    - Printing the total number of cleaned and extracted links.

    Requirements:
    - `crawl4ai` installed and properly configured.
    - An internet connection to access the target site (Yahoo Finance News).

    Expected Output:
    - Total number of cleaned links extracted.
    - Sample of the extracted links.

    """

    browser_config = BrowserConfig(
        headless=True,
        text_mode=True,
        light_mode=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        url_extractor = URLExtractorCrawler(
            crawler=crawler,
            strategy=ScrollExplorationStrategy(
                duration_seconds=2,
                scroll_interval=1.0,
            ),
            run_config=CrawlerRunConfig(
                wait_for="css:body",
                cache_mode=CacheMode.BYPASS,
                session_id="scroller",
                exclude_external_links=True,
                exclude_social_media_links=True,
            )
        )

        extracted_links = await url_extractor.extract(
            url="https://finance.yahoo.com/news/",
            sanitizer=URLSanitizerChain([
                RemoveQueryParametersSanitizer(),
                PrefixSanitizer("https://finance.yahoo.com/news/"),
                RemoveNoneSanitizer(),
            ])
        )

        print(f"Total cleaned links extracted: {len(extracted_links)}")
        print(f"Extracted Links Sample: {extracted_links[:2]}")


if __name__ == "__main__":
    asyncio.run(usage_example())
