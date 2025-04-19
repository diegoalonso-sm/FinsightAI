import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai import BrowserConfig, CacheMode
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

async def yahoo_finance_crawler():

    browser_config = BrowserConfig(
        headless=True,
    )

    url_scorer = KeywordRelevanceScorer(
        keywords=["crawl", "example", "async", "configuration"],
        weight=0.7
    )

    crawling_strategy = BestFirstCrawlingStrategy(
        max_depth=5,
        include_external=False,
        url_scorer=url_scorer,
        max_pages=25,
    )

    run_config = CrawlerRunConfig(
        #deep_crawl_strategy=crawling_strategy,
        cache_mode=CacheMode.BYPASS,
        excluded_tags=['form', 'header', 'footer', 'scripts', 'style'],
        keep_data_attributes=False,
        #exclude_external_links=True,
        #remove_overlay_elements=True,
        #pdf=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        result = await crawler.arun(
            url="https://finance.yahoo.com/news",
            config = run_config,
        )

        if not result.success:
            print(f"Crawl failed: {result.error_message}")
            print(f"Status code: {result.status_code}")

        if result.pdf:
            with open("wikipedia_page.pdf", "wb") as f:
                f.write(result.pdf)

        print(result.cleaned_html)


if __name__ == "__main__":
    asyncio.run(yahoo_finance_crawler())
