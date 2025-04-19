import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai import BrowserConfig, CacheMode
from crawl4ai.async_configs import CrawlerRunConfig


async def yahoo_finance_crawler():

    browser_config = BrowserConfig(
        headless=False,
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        result = await crawler.arun(
            url="https://finance.yahoo.com/news",
            config = run_config,
        )

        print(result.cleaned_html)


if __name__ == "__main__":
    asyncio.run(yahoo_finance_crawler())
