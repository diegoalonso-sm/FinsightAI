import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai import BrowserConfig, CacheMode
from crawl4ai.async_configs import CrawlerRunConfig
# from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
)

# TODO: Considerar utilizar estrategias de streaming para paralelizar el scraping.
# TODO: Revisar por qué no se están imprimiendo correctamente los scores.
# TODO: Probar filtros del tipo SEOFilter y ContentRelevanceFilter.

keywords = {
    "EquityTech Fund": "Technology",
    "GreenEnergy ETF": "Renewable energy",
    "HealthBio Stocks": "Biotechnology",
    "Global Bonds Fund": "Government bonds",
    "CryptoIndex": "Cryptocurrencies",
    "RealEstate REIT": "Real estate investment",
    "Emerging Markets Fund": "Emerging markets",
    "AI & Robotics ETF": "Artificial intelligence",
    "Commodities Basket": "Commodities",
    "Cash Reserve": "Liquidity"
}

async def yahoo_finance_crawler():

    browser_config = BrowserConfig(
        headless=True,
    )

    url_scorer = KeywordRelevanceScorer(
        keywords=[keyword.lower() for keyword in keywords.values()],
        weight=0.7  # Minimum similarity score (0.0 to 1.0)
    )

    filter_chain = FilterChain([
        URLPatternFilter(patterns=["*/news/*"]),
        DomainFilter(allowed_domains=["finance.yahoo.com"]),
    ])

    crawling_strategy = BestFirstCrawlingStrategy(
        max_depth=3,
        include_external=False,
        url_scorer=url_scorer,
        max_pages=100,
        filter_chain=filter_chain,
    )

    run_config = CrawlerRunConfig(
        deep_crawl_strategy=crawling_strategy,
        cache_mode=CacheMode.BYPASS,
        excluded_tags=['form', 'scripts', 'style'],
        keep_data_attributes=False,
        stream=True
        #exclude_external_links=True,
        #remove_overlay_elements=True,
        #pdf=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        results = []

        async for result in await crawler.arun(
            url="https://finance.yahoo.com/news",
            config = run_config,
        ):

            results.append(result)
            score = result.metadata.get("score", 0)
            print(f"Score: {score:.2f} | {result.url}")

            if not result.success:
                print(f"Crawl failed: {result.error_message}")
                print(f"Status code: {result.status_code}")

            if result.pdf:
                with open("wikipedia_page.pdf", "wb") as f:
                    f.write(result.pdf)

        # print(result.cleaned_html)

        print(f"Crawled {len(results)} high-value pages")


if __name__ == "__main__":
    asyncio.run(yahoo_finance_crawler())
