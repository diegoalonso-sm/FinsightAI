import asyncio
import json
from typing import List

from crawl4ai import AsyncWebCrawler
from crawl4ai import BrowserConfig, CacheMode
from crawl4ai.async_configs import CrawlerRunConfig
# from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
import time
from crawl4ai import LLMConfig
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, CrawlResult
from crawl4ai import JsonCssExtractionStrategy
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
        max_depth=3,  # O puedes poner 2 o más si quieres explorar más
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


async def demo_css_structured_extraction_no_schema():

    sample_html = """<div class="article-wrap no-bb" data-testid="article-content-wrapper"> <div class="cover-wrap yf-1rjrr1"> <div class="top-header yf-1rjrr1">  <a class="subtle-link fin-size-small yf-1xqzjha" data-ylk="elm:logo;elmt:link;itc:0;sec:logo-provider;slk:Insider%20Monkey" href="http://www.insidermonkey.com" aria-label="Insider Monkey" title="Insider Monkey" data-rapid_p="154" data-v9y="1"><img src="https://s.yimg.com/ny/api/res/1.2/ztUvb5bBfSnEzDduOrwWyA--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyNjtoPTQ4/https://s.yimg.com/os/creatr-uploaded-images/2020-12/d7df1000-34e4-11eb-b6ae-ac87660fe5ee" alt="Insider Monkey" width="63" height="24" loading="lazy"> </a> </div> <div class="cover-headline yf-1rjrr1"><div class="cover-title yf-1rjrr1">Is Geron Corp. (NASDAQ:GERN) the Most Promising Penny Stock According to Analysts?</div> <label class="type-ui-xxl-reg yf-rtg296"></label></div> </div> <div class="byline yf-1k5w6kz"><div class="byline-attr yf-1k5w6kz"> <div><div class="byline-attr-author yf-1k5w6kz">  Maham Fatima </div> <div class="byline-attr-time-style"> <time class="byline-attr-meta-time" datetime="2025-04-18T15:45:04.000Z" data-timestamp="2025-04-18T15:45:04.000Z">Fri, April 18, 2025 at 11:45 AM GMT-4</time> <span class="byline-attr-mins-read yf-37lelh">5 min read</span></div></div></div> <div class="byline-share yf-1k5w6kz"><div><span class="share-dialog yf-15ypo5z"><div class="menuContainer  yf-33jgs4" style="                    "><button class="tertiary-btn fin-size-medium menuBtn tw-p-1 rounded yf-lf2kw8" data-ylk="elmt:menu;itc:1;elm:btn;sec:consolidated-share-popup;g:92854b00-6457-3342-8b36-54b7730add03;slk:share-menu-open" aria-haspopup="true" aria-controls="menu-10" title="Share links" data-testid="share-link" dialogalignleftvalue="-240px" dialogaligntopvalue="40px" aria-label="Share links" data-rapid_p="155" data-v9y="1"> <div aria-hidden="true" class="icon fin-icon primary-icn sz-x-large yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m16 5-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4zm4 5v11c0 1.1-.9 2-2 2H6a2 2 0 0 1-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3a2 2 0 0 1 2 2"></path></svg></div></button> <div class="dialog-container menu-surface-dialog modal yf-33jgs4" id="menu-10" aria-hidden="true"></div></div></span> <span class="mweb-share-dialog yf-15ypo5z"><button class="icon2-btn fin-size-medium rounded yf-lf2kw8" data-ylk="elm:share;itc:1;sec:consolidated-share-popup;g:92854b00-6457-3342-8b36-54b7730add03;slk:share-menu-open" title="Share Links" aria-label="Share Links" data-rapid_p="156"><div aria-hidden="true" class="icon fin-icon inherit-icn sz-large yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m16 5-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4zm4 5v11c0 1.1-.9 2-2 2H6a2 2 0 0 1-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3a2 2 0 0 1 2 2"></path></svg></div> </button></span></div> </div></div> <div class="body-wrap yf-40hgrf"><h2 class="type-section-sm-bold yf-rtg296">In This Article:</h2> <div class="ticker-list yf-pqeumq"><div style="display: contents; --layout-gutter: 0; --_padding: 0;"><div><div class="scroll-carousel yf-r5lvmz" data-testid="carousel-container"><div class="carousel-top yf-pqeumq"><div style="display: contents; --ticker-name-font-size: var(--font-m); --text-color: var(--text1); --ticker-change-font-weight: var(--font-normal); --ticker-hover2-box-shadow: 0 4px 10px 0 rgba(0, 0, 0, .08); --ticker-hover2-border-color: var(--light-divider);"><span class="ticker-wrapper yf-86iz4a has-follow"><a data-testid="ticker-container" class="ticker medium hover2 border has-follow streaming extraPadding yf-86iz4a" aria-label="002722.SZ" data-ylk="elm:qte;elmt:link;itc:0;sec:ticker-tag-module;slk:002722.SZ" href="/quote/002722.SZ/" title="002722.SZ" data-rapid_p="157" data-v9y="1"> <div class="name yf-86iz4a"><span class="symbol yf-86iz4a">002722.SZ </span> </div> <fin-streamer class="percentChange yf-86iz4a" data-symbol="002722.SZ" data-field="regularMarketChangePercent" data-trend="txt" data-pricehint="2" data-tstyle="default" active=""><span class="txt-positive yf-86iz4a">+0.15%</span></fin-streamer> </a> <div class="follow yf-86iz4a extraPadding"> <div class="menuContainer follow-btn yf-33jgs4" style="                    "><button class="link-btn fin-size-x-small menuBtn rounded yf-lf2kw8" data-ylk="elmt:ticker;itc:1;cid:002722.SZ;elm:intent-follow;sec:article-following;slk:menu-open;ticker:002722.SZ" aria-haspopup="true" aria-controls="menu-13" data-testid="add-to-following" dialogalignleftvalue="0" title="Follow" aria-label="Follow" data-rapid_p="281" data-v9y="1"> <div aria-hidden="true" class="icon fin-icon secondary-icn sz-medium yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m22 9.24-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28z"></path></svg></div></button> <div class="dialog-container yf-33jgs4" id="menu-13" aria-hidden="true" popover="manual"></div></div> <dialog class="no-bb yf-1e59yx3 modal" role="alertdialog" aria-label=""></dialog></div></span></div></div></div></div></div></div>  <div class="body yf-3qln1o">  <div class="atoms-wrapper"> <p class="yf-1090901">We recently published a list of the <strong><a href="https://www.insidermonkey.com/blog/11-most-promising-penny-stocks-according-to-analysts-1508225/" rel="nofollow noopener" target="_blank" data-ylk="slk:11 Most Promising Penny Stocks According to Analysts;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="159" data-v9y="1">11 Most Promising Penny Stocks According to Analysts</a></strong>. In this article, we are going to take a look at where Geron Corp. (NASDAQ:GERN) stands against other promising penny stocks.</p> <p class="yf-1090901">Solus’ Dan Greenhaus, and Invesco’s Brian Levitt together appeared on CNBC’s ‘Closing Bell’ on April 15 to talk about tariffs, market uncertainty, and risk concerns. The discussion started with Dan Greenhaus expressing his belief that many worst-case scenarios are already priced into the market. He acknowledged that he’s cautious but not overly worried. He pointed out recent events, like the exemptions on auto part imports and the 90-day delay on tariff implementation, as evidence that President Trump is listening to advisors and avoiding pushing toward extreme outcomes. Greenhaus attributed these actions to the rebound seen in the stock market. At the same time, he agreed that the administration has been rather inconsistent, in the context of Morgan Stanley’s comment that investors should prepare for more inconsistencies. But he argued that many investors are assuming scenarios closer to the worst rather than the best. He emphasized that while frightening predictions about skyrocketing prices are taking over media right now, these scenarios are unlikely to materialize.</p> <div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-1" class="sdaContainer dv-all sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-1 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250,fluid" data-ad-region="main-dynamic" data-ad-loc="mid_center" style="--placeholder-height: 250px;"></div></div> <p class="yf-1090901">Brian Levitt built on Greenhaus’ optimism while acknowledging the ongoing uncertainty as well. He attributed this uncertainty to the reliance on decisions from the White House rather than traditional policy mechanisms. He compared the current situation to 2018 when markets fell 20% in a quarter before rebounding due to trade pauses and Fed intervention. He cautioned that the current S&amp;P 500 multiples are not at recession levels so there are potential downside risks if uncertainty remains. While Levitt thinks that business investment and consumer confidence metrics show signs of prolonged volatility, Greenhaus further emphasizes that periods of heightened uncertainty often end up presenting long-term investment opportunities. He acknowledged risks such as sudden tariff increases but also encouraged investors to take advantage of these moments when risk premiums rise.</p> <h3 class="header-scroll yf-gn6wdt"><em><strong>Our Methodology</strong></em></h3> <p class="yf-1090901">We sifted through the Finviz stock screener to compile a list of the top penny stocks that were trading below $5 and had the highest analysts’ upside potential (at least 40%). The stocks are ranked in ascending order of their upside potential. We have also added the hedge fund sentiment for each stock, as of Q4 2024, which was sourced from Insider Monkey’s database.</p> </div> <div class="readmore active yf-103i3cu"><button class="secondary-btn fin-size-large readmore-button rounded yf-lf2kw8" data-ylk="elm:readmore;itc:1;sec:content-canvas;slk:Story%20Continues" aria-label="Story Continues" title="Story Continues" data-rapid_p="160" data-v9y="1"> <span>Story Continues</span></button></div> <div class="read-more-wrapper" style="display: block" data-testid="read-more"><p class="yf-1090901"><strong>Note: All data was sourced on April 15.</strong></p><p class="yf-1090901">Why are we interested in the stocks that hedge funds pile into? The reason is simple: our research has shown that we can outperform the market by imitating the top stock picks of the best hedge funds. Our quarterly newsletter’s strategy selects 14 small-cap and large-cap stocks every quarter and has returned 373.4% since May 2014, beating its benchmark by 218 percentage points (<a href="https://www.insidermonkey.com/premium/newsletters/quarterly" rel="nofollow noopener" target="_blank" data-ylk="slk:see more details here;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="161" data-v9y="1"><strong>s</strong><strong>ee more details here</strong></a>).</p><figure class="yf-8xybrv"><div class="image-container yf-g633g8" style="--max-height: 538px;"> <div class="image-wrapper yf-g633g8" style="--aspect-ratio: 960 / 538; --img-max-width: 960px;"><img src="https://s.yimg.com/ny/api/res/1.2/80gShzuL7WOgj5qsS69wfw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTUzOA--/https://media.zenfs.com/en/insidermonkey.com/88303163f16f53972d909fd12e92805d" alt="Is Geron Corp. (NASDAQ:GERN) the Most Promising Penny Stock According to Analysts?" loading="lazy" height="538" width="960" class="yf-g633g8 loaded"></div></div> <figcaption class="yf-8xybrv">Is Geron Corp. (NASDAQ:GERN) the Most Promising Penny Stock According to Analysts?  </figcaption></figure><p class="yf-1090901">A close-up of a laboratory technician in a laboratory, measuring a newly developed biopharmaceutical drug.</p><h3 class="header-scroll yf-gn6wdt">Geron Corp. (NASDAQ:<a href="https://finance.yahoo.com/quote/GERN" data-ylk="slk:GERN;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="162" data-v9y="1"><strong>GERN</strong></a>)</h3><p class="yf-1090901"><strong>Share Price as of April 15: $1.32</strong></p><p class="yf-1090901"><b><i>Number of Hedge Fund Holders: 46</i></b></p><p class="yf-1090901"><b><i>Average Upside Potential as of April 15: 240.91%</i></b></p><p class="yf-1090901">Geron Corp. (NASDAQ:GERN) is a commercial-stage biopharmaceutical company that develops therapeutics for oncology. It offers RYTELO, which is a telomerase inhibitor for the treatment of adult patients with low to intermediate-1 risk myelodysplastic syndromes (lower-risk MDS) with transfusion-dependent anemia. RYTELO was approved in the US in June 2024.</p><div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-2" class="sdaContainer dv-all sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-2 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250" data-ad-region="main-dynamic" data-ad-loc="mid_center_2" style="--placeholder-height: 250px;"></div></div><p class="yf-1090901">Later in August 2024, RYTELO also gained favorable placement in the NCCN guidelines and received a Category 1 treatment recommendation for second-line RS-positive and RS-negative patients. Since its launch in the US, RYTELO made $76.5 million in net product revenue by year-end. In Q4 2024 alone, RYTELO made $47.5 million in net product revenue.</p><p class="yf-1090901">RYTELO has received a positive opinion in Europe, with a final EU approval decision expected in H1 2025. This will potentially lead to a 2026 EU launch. On March 12, Wedbush analyst Robert Driscoll maintained a Buy rating on the stock with a $7 price target. Payers that cover about 80% of US-insured lives have favorable coverage for RYTELO. The US market for eligible lower-risk MDS patients is estimated to be ~15,400 in 2025.</p><p class="yf-1090901">ClearBridge Small Cap Growth Strategy stated the following regarding Geron Corporation (NASDAQ:GERN) in its Q1 2025&nbsp;<a href="https://www.insidermonkey.com/blog/should-you-invest-in-geron-corporation-gern-1503456/" rel="nofollow noopener" target="_blank" data-ylk="slk:investor letter;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="163" data-v9y="1"><strong>investor letter</strong></a>:</p><blockquote class="neo-blockquote yf-1ba2ufg"><p class="yf-1ba2ufg">“We continued to generate a number of compelling new ideas, adding five new investments that we still held at quarter end: Glaukos, Rocket Lab USA, Karman Holdings (through its IPO), Archrock, Hims &amp; Hers and&nbsp;<strong>Geron Corporation</strong>&nbsp;(NASDAQ:GERN).</p> </blockquote><p class="yf-1090901">Overall, GERN <strong><b>ranks 5th </b></strong>on our list of the most promising penny stocks according to analysts. While we acknowledge the growth potential of GERN, our conviction lies in the belief that AI stocks hold great promise for delivering high returns and doing so within a shorter time frame. There is an AI stock that went up since the beginning of 2025, while popular AI stocks lost around 25%. If you are looking for an AI stock that is more promising than GERN but that trades at less than 5 times its earnings, check out our report about the <a href="https://www.insidermonkey.com/blog/undervalued-ai-stock-poised-for-massive-gains-10000-upside-12/" rel="nofollow noopener" target="_blank" data-ylk="slk:cheapest AI stock;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="164" data-v9y="1"><strong>cheapest AI stock</strong></a>.</p><p class="yf-1090901"><strong><b>READ NEXT:&nbsp;</b></strong><a href="https://www.insidermonkey.com/blog/20-best-artificial-intelligence-ai-stocks-to-buy-according-to-analysts-1424545/" rel="nofollow noopener" target="_blank" data-ylk="slk:20 Best AI Stocks To Buy Now;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="165" data-v9y="1"><strong><b>20 Best AI Stocks To Buy Now</b></strong></a><strong><b>&nbsp;and&nbsp;</b></strong><a href="https://www.insidermonkey.com/blog/30-best-stocks-to-invest-in-according-to-billionaires-1471371/" rel="nofollow noopener" target="_blank" data-ylk="slk:30 Best Stocks to Buy Now According to Billionaires;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="166" data-v9y="1"><strong><b>30 Best Stocks to Buy Now According to Billionaires</b></strong></a><strong>.</strong></p><p class="yf-1090901">Disclosure: None. This article is originally published at&nbsp;<a href="https://www.insidermonkey.com/" rel="nofollow noopener" target="_blank" data-ylk="slk:Insider Monkey;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="167" data-v9y="1"><strong><b>Insider Monkey</b></strong></a><strong><b>.</b></strong></p></div>  </div></div> <span class="article-footer yf-10hzt8r"><section class="privacy-container yf-19q4z23 inline" style="--privacy-link-font-weight: var(--font-normal);"><div class="terms-and-privacy small yf-19q4z23 column"><a class="subtle-link fin-size-small privacy-link-terms-link yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/terms?locale=en-US" data-rapid_p="168" data-v9y="1">Terms </a> and <a class="subtle-link fin-size-small privacy-link-privacy-link yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/privacy-policy?locale=en-US" data-rapid_p="169" data-v9y="1">Privacy Policy </a></div>  <div class="link-groups yf-19q4z23 column"> <a class="subtle-link fin-size-small privacy-link-dashboard noUnderline yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/privacy-dashboard?locale=en-US" data-rapid_p="170" data-v9y="1">Privacy Dashboard </a></div> <div class="link-groups yf-19q4z23 column">  <a href="/more-info" class="more-info yf-19q4z23" data-rapid_p="171">More Info</a></div></section></span></div>"""

    schema = JsonCssExtractionStrategy.generate_schema(
        html=sample_html,
        llm_config=LLMConfig(
            provider="openai/gpt-4o-mini",
        ),
        query="From https://finance.yahoo.com/news/geron-corp-nasdaq-gern-most-154504842.html, I have shared a sample of one news div with a title, url, date, short-description, and complete-article. Please generate a schema for this news div and only for the properties I asked for. Please. include the whole article from top to bottom. The schema should be in JSON format and should include the following properties: title, url, date, short-description, complete-article. Please do not include any other properties or information.",
    )

    extraction_strategy = JsonCssExtractionStrategy(schema)
    config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

    async with AsyncWebCrawler() as crawler:
        results: List[CrawlResult] = await crawler.arun(
            "https://finance.yahoo.com/news/geron-corp-nasdaq-gern-most-154504842.html", config=config
        )

        for result in results:
            print(f"URL: {result.url}")
            print(f"Success: {result.success}")
            if result.success:
                data = json.loads(result.extracted_content)
                print(json.dumps(data, indent=2))
            else:
                print("Failed to extract structured data")


async def demo_parallel_crawl():

    urls = [
        "https://finance.yahoo.com/news/docgo-inc-dcgo-best-quality-034635447.html",
        "https://finance.yahoo.com/news/satixfy-communications-ltd-satx-best-191224370.html",
    ]

    sample_html = """<div class="article-wrap no-bb" data-testid="article-content-wrapper"> <div class="cover-wrap yf-1rjrr1"> <div class="top-header yf-1rjrr1">  <a class="subtle-link fin-size-small yf-1xqzjha" data-ylk="elm:logo;elmt:link;itc:0;sec:logo-provider;slk:Insider%20Monkey" href="http://www.insidermonkey.com" aria-label="Insider Monkey" title="Insider Monkey" data-rapid_p="154" data-v9y="1"><img src="https://s.yimg.com/ny/api/res/1.2/ztUvb5bBfSnEzDduOrwWyA--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyNjtoPTQ4/https://s.yimg.com/os/creatr-uploaded-images/2020-12/d7df1000-34e4-11eb-b6ae-ac87660fe5ee" alt="Insider Monkey" width="63" height="24" loading="lazy"> </a> </div> <div class="cover-headline yf-1rjrr1"><div class="cover-title yf-1rjrr1">Is Geron Corp. (NASDAQ:GERN) the Most Promising Penny Stock According to Analysts?</div> <label class="type-ui-xxl-reg yf-rtg296"></label></div> </div> <div class="byline yf-1k5w6kz"><div class="byline-attr yf-1k5w6kz"> <div><div class="byline-attr-author yf-1k5w6kz">  Maham Fatima </div> <div class="byline-attr-time-style"> <time class="byline-attr-meta-time" datetime="2025-04-18T15:45:04.000Z" data-timestamp="2025-04-18T15:45:04.000Z">Fri, April 18, 2025 at 11:45 AM GMT-4</time> <span class="byline-attr-mins-read yf-37lelh">5 min read</span></div></div></div> <div class="byline-share yf-1k5w6kz"><div><span class="share-dialog yf-15ypo5z"><div class="menuContainer  yf-33jgs4" style="                    "><button class="tertiary-btn fin-size-medium menuBtn tw-p-1 rounded yf-lf2kw8" data-ylk="elmt:menu;itc:1;elm:btn;sec:consolidated-share-popup;g:92854b00-6457-3342-8b36-54b7730add03;slk:share-menu-open" aria-haspopup="true" aria-controls="menu-10" title="Share links" data-testid="share-link" dialogalignleftvalue="-240px" dialogaligntopvalue="40px" aria-label="Share links" data-rapid_p="155" data-v9y="1"> <div aria-hidden="true" class="icon fin-icon primary-icn sz-x-large yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m16 5-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4zm4 5v11c0 1.1-.9 2-2 2H6a2 2 0 0 1-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3a2 2 0 0 1 2 2"></path></svg></div></button> <div class="dialog-container menu-surface-dialog modal yf-33jgs4" id="menu-10" aria-hidden="true"></div></div></span> <span class="mweb-share-dialog yf-15ypo5z"><button class="icon2-btn fin-size-medium rounded yf-lf2kw8" data-ylk="elm:share;itc:1;sec:consolidated-share-popup;g:92854b00-6457-3342-8b36-54b7730add03;slk:share-menu-open" title="Share Links" aria-label="Share Links" data-rapid_p="156"><div aria-hidden="true" class="icon fin-icon inherit-icn sz-large yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m16 5-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4zm4 5v11c0 1.1-.9 2-2 2H6a2 2 0 0 1-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3a2 2 0 0 1 2 2"></path></svg></div> </button></span></div> </div></div> <div class="body-wrap yf-40hgrf"><h2 class="type-section-sm-bold yf-rtg296">In This Article:</h2> <div class="ticker-list yf-pqeumq"><div style="display: contents; --layout-gutter: 0; --_padding: 0;"><div><div class="scroll-carousel yf-r5lvmz" data-testid="carousel-container"><div class="carousel-top yf-pqeumq"><div style="display: contents; --ticker-name-font-size: var(--font-m); --text-color: var(--text1); --ticker-change-font-weight: var(--font-normal); --ticker-hover2-box-shadow: 0 4px 10px 0 rgba(0, 0, 0, .08); --ticker-hover2-border-color: var(--light-divider);"><span class="ticker-wrapper yf-86iz4a has-follow"><a data-testid="ticker-container" class="ticker medium hover2 border has-follow streaming extraPadding yf-86iz4a" aria-label="002722.SZ" data-ylk="elm:qte;elmt:link;itc:0;sec:ticker-tag-module;slk:002722.SZ" href="/quote/002722.SZ/" title="002722.SZ" data-rapid_p="157" data-v9y="1"> <div class="name yf-86iz4a"><span class="symbol yf-86iz4a">002722.SZ </span> </div> <fin-streamer class="percentChange yf-86iz4a" data-symbol="002722.SZ" data-field="regularMarketChangePercent" data-trend="txt" data-pricehint="2" data-tstyle="default" active=""><span class="txt-positive yf-86iz4a">+0.15%</span></fin-streamer> </a> <div class="follow yf-86iz4a extraPadding"> <div class="menuContainer follow-btn yf-33jgs4" style="                    "><button class="link-btn fin-size-x-small menuBtn rounded yf-lf2kw8" data-ylk="elmt:ticker;itc:1;cid:002722.SZ;elm:intent-follow;sec:article-following;slk:menu-open;ticker:002722.SZ" aria-haspopup="true" aria-controls="menu-13" data-testid="add-to-following" dialogalignleftvalue="0" title="Follow" aria-label="Follow" data-rapid_p="281" data-v9y="1"> <div aria-hidden="true" class="icon fin-icon secondary-icn sz-medium yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m22 9.24-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28z"></path></svg></div></button> <div class="dialog-container yf-33jgs4" id="menu-13" aria-hidden="true" popover="manual"></div></div> <dialog class="no-bb yf-1e59yx3 modal" role="alertdialog" aria-label=""></dialog></div></span></div></div></div></div></div></div>  <div class="body yf-3qln1o">  <div class="atoms-wrapper"> <p class="yf-1090901">We recently published a list of the <strong><a href="https://www.insidermonkey.com/blog/11-most-promising-penny-stocks-according-to-analysts-1508225/" rel="nofollow noopener" target="_blank" data-ylk="slk:11 Most Promising Penny Stocks According to Analysts;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="159" data-v9y="1">11 Most Promising Penny Stocks According to Analysts</a></strong>. In this article, we are going to take a look at where Geron Corp. (NASDAQ:GERN) stands against other promising penny stocks.</p> <p class="yf-1090901">Solus’ Dan Greenhaus, and Invesco’s Brian Levitt together appeared on CNBC’s ‘Closing Bell’ on April 15 to talk about tariffs, market uncertainty, and risk concerns. The discussion started with Dan Greenhaus expressing his belief that many worst-case scenarios are already priced into the market. He acknowledged that he’s cautious but not overly worried. He pointed out recent events, like the exemptions on auto part imports and the 90-day delay on tariff implementation, as evidence that President Trump is listening to advisors and avoiding pushing toward extreme outcomes. Greenhaus attributed these actions to the rebound seen in the stock market. At the same time, he agreed that the administration has been rather inconsistent, in the context of Morgan Stanley’s comment that investors should prepare for more inconsistencies. But he argued that many investors are assuming scenarios closer to the worst rather than the best. He emphasized that while frightening predictions about skyrocketing prices are taking over media right now, these scenarios are unlikely to materialize.</p> <div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-1" class="sdaContainer dv-all sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-1 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250,fluid" data-ad-region="main-dynamic" data-ad-loc="mid_center" style="--placeholder-height: 250px;"></div></div> <p class="yf-1090901">Brian Levitt built on Greenhaus’ optimism while acknowledging the ongoing uncertainty as well. He attributed this uncertainty to the reliance on decisions from the White House rather than traditional policy mechanisms. He compared the current situation to 2018 when markets fell 20% in a quarter before rebounding due to trade pauses and Fed intervention. He cautioned that the current S&amp;P 500 multiples are not at recession levels so there are potential downside risks if uncertainty remains. While Levitt thinks that business investment and consumer confidence metrics show signs of prolonged volatility, Greenhaus further emphasizes that periods of heightened uncertainty often end up presenting long-term investment opportunities. He acknowledged risks such as sudden tariff increases but also encouraged investors to take advantage of these moments when risk premiums rise.</p> <h3 class="header-scroll yf-gn6wdt"><em><strong>Our Methodology</strong></em></h3> <p class="yf-1090901">We sifted through the Finviz stock screener to compile a list of the top penny stocks that were trading below $5 and had the highest analysts’ upside potential (at least 40%). The stocks are ranked in ascending order of their upside potential. We have also added the hedge fund sentiment for each stock, as of Q4 2024, which was sourced from Insider Monkey’s database.</p> </div> <div class="readmore active yf-103i3cu"><button class="secondary-btn fin-size-large readmore-button rounded yf-lf2kw8" data-ylk="elm:readmore;itc:1;sec:content-canvas;slk:Story%20Continues" aria-label="Story Continues" title="Story Continues" data-rapid_p="160" data-v9y="1"> <span>Story Continues</span></button></div> <div class="read-more-wrapper" style="display: block" data-testid="read-more"><p class="yf-1090901"><strong>Note: All data was sourced on April 15.</strong></p><p class="yf-1090901">Why are we interested in the stocks that hedge funds pile into? The reason is simple: our research has shown that we can outperform the market by imitating the top stock picks of the best hedge funds. Our quarterly newsletter’s strategy selects 14 small-cap and large-cap stocks every quarter and has returned 373.4% since May 2014, beating its benchmark by 218 percentage points (<a href="https://www.insidermonkey.com/premium/newsletters/quarterly" rel="nofollow noopener" target="_blank" data-ylk="slk:see more details here;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="161" data-v9y="1"><strong>s</strong><strong>ee more details here</strong></a>).</p><figure class="yf-8xybrv"><div class="image-container yf-g633g8" style="--max-height: 538px;"> <div class="image-wrapper yf-g633g8" style="--aspect-ratio: 960 / 538; --img-max-width: 960px;"><img src="https://s.yimg.com/ny/api/res/1.2/80gShzuL7WOgj5qsS69wfw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTUzOA--/https://media.zenfs.com/en/insidermonkey.com/88303163f16f53972d909fd12e92805d" alt="Is Geron Corp. (NASDAQ:GERN) the Most Promising Penny Stock According to Analysts?" loading="lazy" height="538" width="960" class="yf-g633g8 loaded"></div></div> <figcaption class="yf-8xybrv">Is Geron Corp. (NASDAQ:GERN) the Most Promising Penny Stock According to Analysts?  </figcaption></figure><p class="yf-1090901">A close-up of a laboratory technician in a laboratory, measuring a newly developed biopharmaceutical drug.</p><h3 class="header-scroll yf-gn6wdt">Geron Corp. (NASDAQ:<a href="https://finance.yahoo.com/quote/GERN" data-ylk="slk:GERN;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="162" data-v9y="1"><strong>GERN</strong></a>)</h3><p class="yf-1090901"><strong>Share Price as of April 15: $1.32</strong></p><p class="yf-1090901"><b><i>Number of Hedge Fund Holders: 46</i></b></p><p class="yf-1090901"><b><i>Average Upside Potential as of April 15: 240.91%</i></b></p><p class="yf-1090901">Geron Corp. (NASDAQ:GERN) is a commercial-stage biopharmaceutical company that develops therapeutics for oncology. It offers RYTELO, which is a telomerase inhibitor for the treatment of adult patients with low to intermediate-1 risk myelodysplastic syndromes (lower-risk MDS) with transfusion-dependent anemia. RYTELO was approved in the US in June 2024.</p><div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-2" class="sdaContainer dv-all sda-INARTICLE-92854b00-6457-3342-8b36-54b7730add03-2 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250" data-ad-region="main-dynamic" data-ad-loc="mid_center_2" style="--placeholder-height: 250px;"></div></div><p class="yf-1090901">Later in August 2024, RYTELO also gained favorable placement in the NCCN guidelines and received a Category 1 treatment recommendation for second-line RS-positive and RS-negative patients. Since its launch in the US, RYTELO made $76.5 million in net product revenue by year-end. In Q4 2024 alone, RYTELO made $47.5 million in net product revenue.</p><p class="yf-1090901">RYTELO has received a positive opinion in Europe, with a final EU approval decision expected in H1 2025. This will potentially lead to a 2026 EU launch. On March 12, Wedbush analyst Robert Driscoll maintained a Buy rating on the stock with a $7 price target. Payers that cover about 80% of US-insured lives have favorable coverage for RYTELO. The US market for eligible lower-risk MDS patients is estimated to be ~15,400 in 2025.</p><p class="yf-1090901">ClearBridge Small Cap Growth Strategy stated the following regarding Geron Corporation (NASDAQ:GERN) in its Q1 2025&nbsp;<a href="https://www.insidermonkey.com/blog/should-you-invest-in-geron-corporation-gern-1503456/" rel="nofollow noopener" target="_blank" data-ylk="slk:investor letter;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="163" data-v9y="1"><strong>investor letter</strong></a>:</p><blockquote class="neo-blockquote yf-1ba2ufg"><p class="yf-1ba2ufg">“We continued to generate a number of compelling new ideas, adding five new investments that we still held at quarter end: Glaukos, Rocket Lab USA, Karman Holdings (through its IPO), Archrock, Hims &amp; Hers and&nbsp;<strong>Geron Corporation</strong>&nbsp;(NASDAQ:GERN).</p> </blockquote><p class="yf-1090901">Overall, GERN <strong><b>ranks 5th </b></strong>on our list of the most promising penny stocks according to analysts. While we acknowledge the growth potential of GERN, our conviction lies in the belief that AI stocks hold great promise for delivering high returns and doing so within a shorter time frame. There is an AI stock that went up since the beginning of 2025, while popular AI stocks lost around 25%. If you are looking for an AI stock that is more promising than GERN but that trades at less than 5 times its earnings, check out our report about the <a href="https://www.insidermonkey.com/blog/undervalued-ai-stock-poised-for-massive-gains-10000-upside-12/" rel="nofollow noopener" target="_blank" data-ylk="slk:cheapest AI stock;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="164" data-v9y="1"><strong>cheapest AI stock</strong></a>.</p><p class="yf-1090901"><strong><b>READ NEXT:&nbsp;</b></strong><a href="https://www.insidermonkey.com/blog/20-best-artificial-intelligence-ai-stocks-to-buy-according-to-analysts-1424545/" rel="nofollow noopener" target="_blank" data-ylk="slk:20 Best AI Stocks To Buy Now;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="165" data-v9y="1"><strong><b>20 Best AI Stocks To Buy Now</b></strong></a><strong><b>&nbsp;and&nbsp;</b></strong><a href="https://www.insidermonkey.com/blog/30-best-stocks-to-invest-in-according-to-billionaires-1471371/" rel="nofollow noopener" target="_blank" data-ylk="slk:30 Best Stocks to Buy Now According to Billionaires;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="166" data-v9y="1"><strong><b>30 Best Stocks to Buy Now According to Billionaires</b></strong></a><strong>.</strong></p><p class="yf-1090901">Disclosure: None. This article is originally published at&nbsp;<a href="https://www.insidermonkey.com/" rel="nofollow noopener" target="_blank" data-ylk="slk:Insider Monkey;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="167" data-v9y="1"><strong><b>Insider Monkey</b></strong></a><strong><b>.</b></strong></p></div>  </div></div> <span class="article-footer yf-10hzt8r"><section class="privacy-container yf-19q4z23 inline" style="--privacy-link-font-weight: var(--font-normal);"><div class="terms-and-privacy small yf-19q4z23 column"><a class="subtle-link fin-size-small privacy-link-terms-link yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/terms?locale=en-US" data-rapid_p="168" data-v9y="1">Terms </a> and <a class="subtle-link fin-size-small privacy-link-privacy-link yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/privacy-policy?locale=en-US" data-rapid_p="169" data-v9y="1">Privacy Policy </a></div>  <div class="link-groups yf-19q4z23 column"> <a class="subtle-link fin-size-small privacy-link-dashboard noUnderline yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/privacy-dashboard?locale=en-US" data-rapid_p="170" data-v9y="1">Privacy Dashboard </a></div> <div class="link-groups yf-19q4z23 column">  <a href="/more-info" class="more-info yf-19q4z23" data-rapid_p="171">More Info</a></div></section></span></div>"""

    schema = JsonCssExtractionStrategy.generate_schema(
        html=sample_html,
        llm_config=LLMConfig(
            provider="openai/gpt-4o-mini",
        ),
        query="From https://finance.yahoo.com/news/geron-corp-nasdaq-gern-most-154504842.html, I have shared a sample of one news div with a title, url, date, short-description, and complete-article. Please generate a schema for this news div and only for the properties I asked for. Please. include the whole article from top to bottom. The schema should be in JSON format and should include the following properties: title, url, date, short-description, complete-article. Please do not include any other properties or information. The links has to be refering to the news in the page. E.g. https://finance.yahoo.com/news/geron-corp-nasdaq-gern-most-154504842.html",
    )

    extraction_strategy = JsonCssExtractionStrategy(schema)
    config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

    async with AsyncWebCrawler() as crawler:

        results: List[CrawlResult] = await crawler.arun_many(
            urls=urls,
            config=config,
        )

        for result in results:

            print(f"URL: {result.url}")
            print(f"Success: {result.success}")

            if result.success:

                data = json.loads(result.extracted_content)
                print(json.dumps(data, indent=2))

            else:
                print("Failed to extract structured data")


if __name__ == "__main__":

    # asyncio.run(yahoo_finance_crawler())
    #  asyncio.run(simple_scroll_time("https://finance.yahoo.com/news", duration_seconds=5))

    #asyncio.run(scroll_and_bestfirst_crawl(
        #url="https://finance.yahoo.com/news",
        #duration_seconds=45  # Cambia este tiempo de scroll como quieras
    #))

    #asyncio.run(demo_css_structured_extraction_no_schema())
    asyncio.run(demo_parallel_crawl())
