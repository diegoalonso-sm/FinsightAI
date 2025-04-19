import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai import BrowserConfig, CacheMode
from crawl4ai.async_configs import CrawlerRunConfig
# from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
import time

from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
)

# TODO: Considerar utilizar estrategias de streaming para paralelizar el scraping.
# TODO: Revisar por qué no se están imprimiendo correctamente los scores.
# TODO: Probar filtros del tipo SEOFilter y ContentRelevanceFilter.
# TODO: En caso de fallar el crawler para un URL, lanzar una excepción.


async def simple_scroll_time(url, duration_seconds=15):

    session_id = "scroll_session"

    browser_config = BrowserConfig(
        headless=False,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        config_initial = CrawlerRunConfig(
            wait_for="css:body",
            session_id=session_id,
            cache_mode=CacheMode.BYPASS,
        )

        result = await crawler.arun(url=url, config=config_initial)

        print(f"🌐 Página cargada. Scrolleando durante {duration_seconds} segundos...")

        start_time = time.time()

        scroll_count = 0

        while (time.time() - start_time) < duration_seconds:
            scroll_js = "window.scrollTo(0, document.body.scrollHeight);"

            config_scroll = CrawlerRunConfig(
                session_id=session_id,
                js_code=scroll_js,
                js_only=True,
                cache_mode=CacheMode.BYPASS,
            )

            await crawler.arun(url=url, config=config_scroll)
            scroll_count += 1
            print(f"🖱️ Scroll número {scroll_count} hecho.")

            await asyncio.sleep(1)  # Esperar 1 segundo entre scrolls (puedes ajustar si quieres más rápido o lento)

        print(f"🎯 Scrolling finalizado tras {scroll_count} scrolls en {duration_seconds} segundos.")

        print(result.links)


async def scroll_and_bestfirst_crawl(url, duration_seconds=15):
    session_id = "scroll_session"

    browser_config = BrowserConfig(
        headless=False,
        text_mode=True,
        light_mode=True,
    )

    filter_chain = FilterChain([
        URLPatternFilter(patterns=["*/news/*"]),
        DomainFilter(
            allowed_domains=["finance.yahoo.com"],
        ),
    ])

    crawling_strategy = BestFirstCrawlingStrategy(
        max_depth=1,  # O puedes poner 2 o más si quieres explorar más
        include_external=False,
        filter_chain=filter_chain,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        # 1. Cargar página inicial
        config_initial = CrawlerRunConfig(
            wait_for="css:body",
            session_id=session_id,
            cache_mode=CacheMode.BYPASS,
        )
        await crawler.arun(url=url, config=config_initial)

        print(f"🌐 Página cargada. Iniciando scroll durante {duration_seconds} segundos...")

        # 2. Scroll automático durante X segundos
        start_time = time.time()
        scroll_count = 0

        while (time.time() - start_time) < duration_seconds:
            scroll_js = "window.scrollTo(0, document.body.scrollHeight);"

            config_scroll = CrawlerRunConfig(
                session_id=session_id,
                js_code=scroll_js,
                js_only=True,  # muy importante: no recargar la página
                cache_mode=CacheMode.BYPASS,
            )
            await crawler.arun(url=url, config=config_scroll)
            scroll_count += 1
            print(f"🖱️ Scroll número {scroll_count} hecho.")

            await asyncio.sleep(1)  # Esperar 1 segundo entre scrolls

        print(f"🎯 Scroll terminado después de {scroll_count} scrolls.")
        print("🚀 Ahora usando BestFirstCrawlingStrategy sobre la página ya cargada...")

        # 3. Deep crawl sobre el DOM scrolleado (no recargar nada nuevo)
        deep_crawl_config = CrawlerRunConfig(
            session_id=session_id,    # ⚡ misma sesión
            deep_crawl_strategy=crawling_strategy,
            js_only=True,             # ⚡ no recargar, solo seguir en DOM actual
            cache_mode=CacheMode.BYPASS,
            stream=True,
            word_count_threshold=200,
            excluded_tags=['form', 'scripts', 'style'],
            keep_data_attributes=False,
        )

        results = []

        async for result in await crawler.arun(url=url, config=deep_crawl_config):
            results.append(result)
            score = result.metadata.get("score", 0)
            print(f"Score: {score:.2f} | {result.url}")

            if not result.success:
                print(f"Crawl failed: {result.error_message}")
                print(f"Status code: {result.status_code}")

        print(f"📄 Crawled {len(results)} high-value pages desde la página ya scrolleada.")

        return results


async def yahoo_finance_crawler():

    browser_config = BrowserConfig(
        headless=True,
        text_mode=True,
        light_mode=True,
    )

    filter_chain = FilterChain([
        URLPatternFilter(patterns=["*/news/*"]),
        DomainFilter(
            allowed_domains=[
                "finance.yahoo.com"
            ],
        ),
    ])

    crawling_strategy = BestFirstCrawlingStrategy(
        max_depth=2,
        include_external=False,
        # max_pages=100,
        filter_chain=filter_chain,
    )

    run_config = CrawlerRunConfig(
        word_count_threshold=200,
        deep_crawl_strategy=crawling_strategy,
        cache_mode=CacheMode.BYPASS,
        excluded_tags=['form', 'scripts', 'style'],
        keep_data_attributes=False,
        stream=True,
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

    # asyncio.run(yahoo_finance_crawler())
    #  asyncio.run(simple_scroll_time("https://finance.yahoo.com/news", duration_seconds=5))

    asyncio.run(scroll_and_bestfirst_crawl(
        url="https://finance.yahoo.com/news",
        duration_seconds=45  # Cambia este tiempo de scroll como quieras
    ))