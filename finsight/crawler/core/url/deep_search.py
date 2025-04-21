import asyncio
from typing import List

from crawl4ai import AsyncWebCrawler
from crawl4ai import CacheMode
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter, DomainFilter

from finsight.crawler.core.url.base import ExplorationStrategy, URLExtractorCrawler

class DeepSearchStrategy(ExplorationStrategy):

    """
    Exploration strategy that performs a deep crawl prioritizing pages based on keyword relevance.
    It uses Best-First Search with specific URL/domain filters.

    """

    def __init__(self, allowed_domains: List[str], url_patterns: List[str], max_depth: int = 3, max_pages: int = 100):

        """
        Initialize the best-first keyword exploration strategy.

        :param allowed_domains: List of allowed domains for the crawl.
        :type allowed_domains: List[str]

        :param url_patterns: List of URL patterns to match during crawling.
        :type url_patterns: List[str]

        :param max_depth: Maximum crawl depth from the starting URL.
        :type max_depth: int

        :param max_pages: Maximum number of pages to crawl.
        :type max_pages: int

        """

        self.allowed_domains = allowed_domains
        self.url_patterns = url_patterns
        self.max_depth = max_depth
        self.max_pages = max_pages

    async def explore(self, crawler: AsyncWebCrawler, url: str, session_id: str) -> List[str]:

        """
        Explore the website deeply and extract links based on keyword scoring.

        :param crawler: The crawler instance.
        :type crawler: AsyncWebCrawler

        :param url: Starting URL to explore.
        :type url: str

        :param session_id: Browser session ID.
        :type session_id: str

        :return: List of extracted and prioritized URLs.
        :rtype: List[str]

        """

        config = CrawlerRunConfig(
            session_id=session_id,
            deep_crawl_strategy=BestFirstCrawlingStrategy(
                max_depth=self.max_depth,
                include_external=False,
                max_pages=self.max_pages,
                filter_chain=FilterChain([
                    URLPatternFilter(patterns=self.url_patterns),
                    DomainFilter(allowed_domains=self.allowed_domains),
                ]),
            ),
            cache_mode=CacheMode.BYPASS,
            stream=True,
            excluded_tags=['form', 'scripts', 'style'],
            keep_data_attributes=False,
        )

        extracted_links = []

        async for result in await crawler.arun(url=url, config=config):

            if result.success and hasattr(result, 'url'):
                extracted_links.append(result.url)

        return extracted_links


async def usage_example() -> None:

    """
    Example usage of the URLExtractorCrawler with BestFirstKeywordExplorationStrategy.

    This example demonstrates:
    - Setting up a deep crawling strategy prioritizing financial news based on keyword relevance.
    - Filtering URLs by pattern and domain restrictions.
    - Streaming results and printing their relevance scores.
    - Collecting and printing the extracted URLs.

    Requirements:
    - `crawl4ai` installed and properly configured.
    - An internet connection to access the target site (Yahoo Finance News).

    Expected Output:
    - Scores and URLs printed during crawling.
    - Total number of high-value pages crawled.
    - Sample of extracted links.

    """

    browser_config = BrowserConfig(
        headless=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        url_extractor = URLExtractorCrawler(
            crawler=crawler,
            strategy=DeepSearchStrategy(
                allowed_domains=["finance.yahoo.com"],
                url_patterns=["*/news/*"],
                max_depth=2,
                max_pages=10,
            ),
            run_config=CrawlerRunConfig(
                wait_for="css:body",
                cache_mode=CacheMode.BYPASS,
            )
        )

        extracted_links = await url_extractor.extract(
            url="https://finance.yahoo.com/news/",
        )

        print(f"\nTotal cleaned links extracted: {len(extracted_links)}")
        print(f"Extracted Links Sample: {extracted_links[:2]}")


if __name__ == "__main__":
    asyncio.run(usage_example())
