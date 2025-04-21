import asyncio
import json
from typing import List

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai import BrowserConfig, JsonCssExtractionStrategy, LLMExtractionStrategy, LLMConfig


class StructuredExtractor:

    """
    Extracts structured data from a list of URLs using a specified extraction strategy.

    This class uses an AsyncWebCrawler instance to navigate to each URL and extract
    structured content based on a given Crawl4AI extraction strategy.

    """

    def __init__(self, crawler: AsyncWebCrawler, extraction_strategy: JsonCssExtractionStrategy | LLMExtractionStrategy):

        """
        Initialize the StructuredExtractor with a crawler and an extraction strategy.

        :param crawler: An instance of AsyncWebCrawler used to perform the asynchronous web crawling.
        :type crawler: AsyncWebCrawler

        :param extraction_strategy: The extraction strategy defining how to parse the HTML content.
        :type extraction_strategy: JsonCssExtractionStrategy or LLMExtractionStrategy

        """

        self.crawler = crawler
        self.extraction_strategy = extraction_strategy

    async def extract(self, urls: List[str]) -> List[dict]:

        """
        Asynchronously extracts structured data from a list of URLs.

        For each URL, the method uses the crawler to fetch and parse the page content
        according to the defined extraction strategy. Only successful extractions are appended
        to the result list.

        :param urls: A list of URLs to crawl and extract structured data from.
        :type urls: List[str]

        :return: A list of dictionaries containing the structured data extracted from each URL.
        :rtype: List[dict]

        """

        structured_data = []

        for url in urls:

            result = await self.crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    magic=True,
                    simulate_user=True,
                    override_navigator=True,
                    wait_for="css:body",
                    extraction_strategy=self.extraction_strategy,
                    check_robots_txt=True,
                )
            )

            if result.success:
                content = result.extracted_content
                json_data = json.loads(content)
                json_data[0]["url"] = result.url
                structured_data += json_data

        return structured_data


async def usage_example() -> None:

    """
    Demonstrates how to use the StructuredExtractor to crawl and extract structured financial news articles.

    This example:
    - Defines a list of URLs to extract financial news from.
    - Provides a sample HTML block from a representative article.
    - Defines a LLM extraction query specifying the target fields.
    - Configures the browser for headless, text-mode crawling.
    - Instantiates a StructuredExtractor with a dynamically generated extraction schema.
    - Extracts and prints the structured data in JSON format.

    Requirements:
    - An active LLM provider (e.g., OpenAI) accessible for schema generation.
    - A valid API key for the LLM provider configured in the environment.
    - The crawl4ai library installed and properly configured.

    Expected output:
    A list of JSON objects, each representing a financial news article with fields:
    - `title` (string): The article's title.
    - `date` (string): The publication date.
    - `full-article` (string): The full-text content of the article.

    """

    urls = [
        'https://finance.yahoo.com/news/jay-powell-made-it-clear-fed-is-not-going-to-rescue-markets-080051450.html'
        'https://finance.yahoo.com/news/live/live-president-trump-reiterates-threat-of-25-tariffs-on-canada-mexico-as-deadline-looms-191201171.html',
        'https://finance.yahoo.com/news/netflix-praised-as-cleanest-story-in-tech-as-latest-earnings-report-brushes-off-macro-worries-154219532.html',
    ]

    sample_html = """<div class="article-wrap no-bb" data-testid="article-content-wrapper"> <div class="cover-wrap yf-1rjrr1"> <div class="top-header yf-1rjrr1">  <a class="subtle-link fin-size-small yf-1xqzjha" data-ylk="elm:logo;elmt:link;itc:0;sec:logo-provider;slk:Insider%20Monkey" href="https://www.insidermonkey.com" aria-label="Insider Monkey" title="Insider Monkey" data-rapid_p="145" data-v9y="1"><img src="https://s.yimg.com/ny/api/res/1.2/ztUvb5bBfSnEzDduOrwWyA--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyNjtoPTQ4/https://s.yimg.com/os/creatr-uploaded-images/2020-12/d7df1000-34e4-11eb-b6ae-ac87660fe5ee" alt="Insider Monkey" width="63" height="24" loading="lazy"> </a> </div> <div class="cover-headline yf-1rjrr1"><div class="cover-title yf-1rjrr1">Why Amazon.com (AMZN) Is the Best Blue Chip Stock to Buy According to Billionaires</div> <label class="type-ui-xxl-reg yf-rtg296"></label></div> </div> <div class="byline yf-1k5w6kz"><div class="byline-attr yf-1k5w6kz"> <div><div class="byline-attr-author yf-1k5w6kz">  Noor Ul Ain Rehman </div> <div class="byline-attr-time-style"> <time class="byline-attr-meta-time" datetime="2025-04-19T15:15:27.000Z" data-timestamp="2025-04-19T15:15:27.000Z">Sat, April 19, 2025 at 11:15 AM GMT-4</time> <span class="byline-attr-mins-read yf-37lelh">6 min read</span></div></div></div> <div class="byline-share yf-1k5w6kz"><div><span class="share-dialog yf-15ypo5z"><div class="menuContainer  yf-33jgs4" style="                    "><button class="tertiary-btn fin-size-medium menuBtn tw-p-1 rounded yf-lf2kw8" data-ylk="elmt:menu;itc:1;elm:btn;sec:consolidated-share-popup;g:a355dbf5-4944-3e60-89bf-b45bc8e0e441;slk:share-menu-open" aria-haspopup="true" aria-controls="menu-76" title="Share links" data-testid="share-link" dialogalignleftvalue="-240px" dialogaligntopvalue="40px" aria-label="Share links" data-rapid_p="146" data-v9y="1"> <div aria-hidden="true" class="icon fin-icon primary-icn sz-x-large yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m16 5-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4zm4 5v11c0 1.1-.9 2-2 2H6a2 2 0 0 1-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3a2 2 0 0 1 2 2"></path></svg></div></button> <div class="dialog-container menu-surface-dialog modal yf-33jgs4" id="menu-76" aria-hidden="true"></div></div></span> <span class="mweb-share-dialog yf-15ypo5z"><button class="icon2-btn fin-size-medium rounded yf-lf2kw8" data-ylk="elm:share;itc:1;sec:consolidated-share-popup;g:a355dbf5-4944-3e60-89bf-b45bc8e0e441;slk:share-menu-open" title="Share Links" aria-label="Share Links" data-rapid_p="147"><div aria-hidden="true" class="icon fin-icon inherit-icn sz-large yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m16 5-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4zm4 5v11c0 1.1-.9 2-2 2H6a2 2 0 0 1-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3a2 2 0 0 1 2 2"></path></svg></div> </button></span></div> </div></div> <div class="body-wrap yf-40hgrf"><h2 class="type-section-sm-bold yf-rtg296">In This Article:</h2> <div class="ticker-list yf-pqeumq"><div style="display: contents; --layout-gutter: 0; --_padding: 0;"><div><div class="scroll-carousel yf-r5lvmz" data-testid="carousel-container"><div class="carousel-top yf-pqeumq"><div style="display: contents; --ticker-name-font-size: var(--font-m); --text-color: var(--text1); --ticker-change-font-weight: var(--font-normal); --ticker-hover2-box-shadow: 0 4px 10px 0 rgba(0, 0, 0, .08); --ticker-hover2-border-color: var(--light-divider);"><span class="ticker-wrapper yf-86iz4a has-follow"><a data-testid="ticker-container" class="ticker medium hover2 border has-follow streaming extraPadding yf-86iz4a" aria-label="AMZN" data-ylk="elm:qte;elmt:link;itc:0;sec:ticker-tag-module;slk:AMZN" href="/quote/AMZN/" title="AMZN" data-rapid_p="148" data-v9y="1"> <div class="name yf-86iz4a"><span class="symbol yf-86iz4a">AMZN </span> </div> <fin-streamer class="percentChange yf-86iz4a" data-symbol="AMZN" data-field="regularMarketChangePercent" data-trend="txt" data-pricehint="2" data-tstyle="default" active=""><span class="txt-negative yf-86iz4a">-0.98%</span></fin-streamer> </a> <div class="follow yf-86iz4a extraPadding"> <div class="menuContainer follow-btn yf-33jgs4" style="                    "><button class="link-btn fin-size-x-small menuBtn rounded yf-lf2kw8" data-ylk="elmt:ticker;itc:1;cid:AMZN;elm:intent-follow;sec:article-following;slk:menu-open;ticker:AMZN" aria-haspopup="true" aria-controls="menu-27" data-testid="add-to-following" dialogalignleftvalue="0" title="Follow" aria-label="Follow" data-rapid_p="275" data-v9y="1"> <div aria-hidden="true" class="icon fin-icon secondary-icn sz-medium yf-9qlxtu"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m22 9.24-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28z"></path></svg></div></button> <div class="dialog-container yf-33jgs4" id="menu-27" aria-hidden="true" popover="manual"></div></div> <dialog class="no-bb yf-1e59yx3 modal" role="alertdialog" aria-label=""></dialog></div></span></div></div></div></div></div></div>  <div class="body yf-3qln1o">  <div class="atoms-wrapper"> <p class="yf-1090901">We recently published a list of <strong><a href="https://www.insidermonkey.com/blog/15-best-blue-chip-stocks-to-buy-according-to-billionaires-1506963/" rel="nofollow noopener" target="_blank" data-ylk="slk:15 Best Blue Chip Stocks to Buy According to Billionaires;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="150" data-v9y="1">15 Best Blue Chip Stocks to Buy According to Billionaires</a></strong>. In this article, we are going to take a look at where Amazon.com, Inc. (NASDAQ:<a class="link " href="https://finance.yahoo.com/quote/AMZN" data-ylk="slk:AMZN;elm:context_link;itc:0;sec:content-canvas" data-rapid_p="151" data-v9y="1">AMZN</a>) stands against other best blue chip stocks to buy according to billionaires.</p> <h2 class="header-scroll yf-gn6wdt">Is A Potential Trade War on the Horizon?</h2> <p class="yf-1090901">The US stock market is showing volatility after President Donald Trump’s recent announcement of sweeping 10% tariffs on all US trading partners and higher tariffs on countries with a trade deficit with the US.</p> <p class="yf-1090901">Economists and investors believe President Trump’s tariff policies could potentially lead to a trade war with America’s trading partners, propelling inflation even higher. These two factors could plunge the US into an economic slowdown, and the markets could potentially sell off quickly if a recession materializes among its looming threats.</p> <div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-1" class="sdaContainer dv-all sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-1 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250,fluid" data-ad-region="main-dynamic" data-ad-loc="mid_center" style="--placeholder-height: 250px;"></div></div> <p class="yf-1090901">On April 10, CNBC reported that stock prices rose sharply a day before after declining for four days straight following President Trump’s announcement of a pause in a significant part of his tariff plan. The White House said that Democratic lawmakers were indulged in partisan games by inquiring if any stock market purchases conducted in recent days were undertaken with prior knowledge of the fact that President Trump would authorize a pause in his tariff plans. Trump announced higher tariffs on China even after he announced a 90-day pause for steeper-than-baseline rates for several other countries.</p> <p class="yf-1090901"><strong>READ ALSO:&nbsp;<a href="https://www.insidermonkey.com/blog/10-best-medical-stocks-to-buy-according-to-billionaires-1504865/#google_vignette" rel="nofollow noopener" target="_blank" data-ylk="slk:10 Best Medical Stocks to Buy According to Billionaires;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="152" data-v9y="1">10 Best Medical Stocks to Buy According to Billionaires</a>&nbsp;and&nbsp;<a href="https://www.insidermonkey.com/blog/10-best-organic-food-stocks-to-buy-according-to-billionaires-1504667/#google_vignette" rel="nofollow noopener" target="_blank" data-ylk="slk:10 Best Organic Food Stocks to Buy According to Billionaires;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="153" data-v9y="1">10 Best Organic Food Stocks to Buy According to Billionaires</a>.</strong></p> <h2 class="header-scroll yf-gn6wdt">Record High Tariffs in the US</h2> <p class="yf-1090901">On April 11, Erica York, economist and the vice president of federal tax policy at the Tax Foundation’s Center for Federal Tax Policy, talked to CNBC’s “The Exchange” about the ongoing scenario and said that the imposition of around 145% total tariff on Chinese goods would result in a suspension of most trade between the US and China. She said:</p> <blockquote class="neo-blockquote yf-1ba2ufg"><p class="yf-1ba2ufg">“It depends on how narrowly the tariff is applied or how broadly it’s applied, but generally, if you get north of a triple-digit tariff, you are cutting off most trade.”</p> </blockquote> <p class="yf-1090901">She further opined that:</p> <blockquote class="neo-blockquote yf-1ba2ufg"><p class="yf-1ba2ufg">“There may still be some things without any substitutes that companies just have to foot the bill, but for the most part, that cuts it off.”</p> </blockquote> <p class="yf-1090901">The economist said that Trump’s new China tariffs, along with the others he implemented, would raise the average tariff rate to record highs the country hasn’t seen since the 1940s. The current market volatility has created numerous remarkable investment opportunities, so let’s look at the 15 best blue chip stocks to buy according to billionaires.</p> </div> <div class="readmore active yf-103i3cu"><button class="secondary-btn fin-size-large readmore-button rounded yf-lf2kw8" data-ylk="elm:readmore;itc:1;sec:content-canvas;slk:Story%20Continues" aria-label="Story Continues" title="Story Continues" data-rapid_p="154" data-v9y="1"> <span>Story Continues</span></button></div> <div class="read-more-wrapper" style="display: block" data-testid="read-more"><h3 class="header-scroll yf-gn6wdt">Our Methodology</h3><p class="yf-1090901">We reviewed financial media reports and ETFs to compile an initial list of blue chip stocks and selected stocks that have a 5-year revenue growth rate of at least 10%. We have also considered the popularity of these stocks among billionaire investors. These billionaires are founders or managers of some of the world’s leading hedge funds and companies. We also added the number of hedge fund holders for each stock as of fiscal Q4 2024, and&nbsp;sourced the hedge fund sentiment data from Insider Monkey’s database.</p><div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-2" class="sdaContainer dv-all sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-2 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250" data-ad-region="main-dynamic" data-ad-loc="mid_center_2" style="--placeholder-height: 250px;"></div></div><p class="yf-1090901">Why are we interested in the stocks that hedge funds pile into? The reason is simple: our research has shown that we can outperform the market by imitating the top stock picks of the best hedge funds. Our quarterly newsletter’s strategy selects 14 small-cap and large-cap stocks every quarter and has returned 275% since May 2014, beating its benchmark by 150 percentage points (<strong><a href="https://www.insidermonkey.com/premium/newsletters/quarterly" rel="nofollow noopener" target="_blank" data-ylk="slk:see more details here;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="155" data-v9y="1">see more details here</a></strong>).</p><figure class="yf-8xybrv"><div class="image-container yf-g633g8" style="--max-height: 538px;"> <div class="image-wrapper yf-g633g8" style="--aspect-ratio: 960 / 538; --img-max-width: 960px;"><img src="https://s.yimg.com/ny/api/res/1.2/QhvwjVIGKDMb0F4mZThUgQ--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTUzOA--/https://media.zenfs.com/en/insidermonkey.com/226ed9ed0936942adb97f3d56073e411" alt="Amazon.com (AMZN): $14 Billion Stake in Anthropic as Claude Launches $200 AI Subscription" loading="lazy" height="538" width="960" class="yf-g633g8 loaded"></div></div> <figcaption class="yf-8xybrv">Amazon.com (AMZN): $14 Billion Stake in Anthropic as Claude Launches $200 AI Subscription  </figcaption></figure><p class="yf-1090901">A customer entering an internet retail store, illustrating the convenience of online shopping.</p><h3 class="header-scroll yf-gn6wdt"><strong>Amazon.com, Inc. (NASDAQ:<a class="link " href="https://finance.yahoo.com/quote/AMZN" data-ylk="slk:AMZN;elm:context_link;itc:0;sec:content-canvas" data-rapid_p="156" data-v9y="1">AMZN</a>)</strong></h3><p class="yf-1090901"><em><strong>Number of Billionaire Investors: 40</strong></em></p><p class="yf-1090901"><em><strong>Number of Hedge Fund Holders: 339</strong></em></p><p class="yf-1090901">Amazon.com, Inc. (NASDAQ:AMZN) is a multinational technology company that offers online retail shopping services. It operates through the North America, International, and Amazon Web Services (AWS) segments. AWS’s segment covers global sales of storage, computers, databases, and other services for government agencies, academic institutions, startups, and enterprises.</p><div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-3" class="sdaContainer dv-all sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-3 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250" data-ad-region="main-dynamic" data-ad-loc="mid_center_3" style="--placeholder-height: 250px;"></div></div><p class="yf-1090901">The company is investing heavily in AI. Its capital expenditures (capex) for 2025 are anticipated to be around $100 billion, most of which would go to AI. The company also said that falling AI inference expenses would fuel increased AI infrastructure spending.</p><p class="yf-1090901">Amazon.com, Inc.’s (NASDAQ:AMZN) e-commerce standing also lends it a significant competitive advantage, as it holds nearly 38% of all e-commerce sales in the US. According to the Boston Consulting Group, e-commerce is expected to continue growing as a percentage of retail sales, reaching around 41% of global retail sales by 2027. This is anticipated to prove substantially beneficial for Amazon.com, Inc. (NASDAQ:AMZN).</p><div class="wrapper yf-eondll" data-testid="inarticle-ad"><div id="sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-4" class="sdaContainer dv-all sda-INARTICLE-a355dbf5-4944-3e60-89bf-b45bc8e0e441-4 yf-ee3idm overflow margin visible placeholder" data-testid="ad-container" data-ad-unit="/22888152279/us/yfin/ros/dt/us_yfin_ros_dt_mid_center" data-ad-size="970x250,728x90,300x250" data-ad-region="main-dynamic" data-ad-loc="mid_center_4" style="--placeholder-height: 250px;"></div></div><p class="yf-1090901">On April 10, Telsey Advisory analyst Joe Feldman maintained a Buy rating on Amazon.com, Inc. (NASDAQ:AMZN) and set a price target of $275.00. Analysts are bullish on the stock, and its median price target of $184.87 implies an upside of 43.88% from current levels.</p><p class="yf-1090901">Ariel Appreciation Fund stated the following regarding Amazon.com, Inc. (NASDAQ:AMZN) in its Q4 2024 investor <strong><a class="link " href="https://www.insidermonkey.com/blog/rga-investment-advisors-q4-2024-investor-letter-1443326/" rel="nofollow noopener" target="_blank" data-ylk="slk:letter;elm:context_link;itc:0;sec:content-canvas" data-rapid_p="157" data-v9y="1">letter</a></strong>:</p><blockquote class="neo-blockquote yf-1ba2ufg"><p class="yf-1ba2ufg">“During the quarter, we initiated three new investments, each in companies we have followed closely for a considerable time. At various points, we viewed them as missed opportunities; however, our experience with Mr. Market has taught us that patience often creates inevitable entry points. This quarter, some exciting opportunities presented themselves. The three investments are Amazon.com, Inc. (NASDAQ:AMZN), Diageo (NYSE: DEO), and Uber (NASDAQ: UBER). We will discuss each in detail below.</p> </blockquote><p class="yf-1090901">Overall, AMZN <b>ranks 1st</b> on our list of the best blue chip stocks to buy according to billionaires. While we acknowledge the potential for AMZN as an investment, our conviction lies in the belief that some AI stocks hold greater promise for delivering higher returns and doing so within a shorter time frame. There is an AI stock that went up since the beginning of 2025, while popular AI stocks lost around 25%. If you are looking for an AI stock that is more promising than AMZN but trades at less than 5 times its earnings, check out our report about this <a href="https://www.insidermonkey.com/blog/undervalued-ai-stock-poised-for-massive-gains-10000-upside-18/" rel="nofollow noopener" target="_blank" data-ylk="slk:cheapest AI stock;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="158" data-v9y="1"><b>cheapest AI stock</b></a><b>.</b></p><p class="yf-1090901"><b>READ NEXT:&nbsp;</b><a href="https://www.insidermonkey.com/blog/20-best-artificial-intelligence-ai-stocks-to-buy-according-to-analysts-1424545/" rel="nofollow noopener" target="_blank" data-ylk="slk:20 Best AI Stocks To Buy Now;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="159" data-v9y="1"><b>20 Best AI Stocks To Buy Now</b></a><b>&nbsp;and&nbsp;</b><a href="https://www.insidermonkey.com/blog/30-best-stocks-to-invest-in-according-to-billionaires-1471371/" rel="nofollow noopener" target="_blank" data-ylk="slk:30 Best Stocks to Buy Now According to Billionaires;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="160" data-v9y="1"><b>30 Best Stocks to Buy Now According to Billionaires</b></a>.</p><p class="yf-1090901">Disclosure: None. This article is originally published at&nbsp;<a href="https://www.insidermonkey.com/" rel="nofollow noopener" target="_blank" data-ylk="slk:Insider Monkey;elm:context_link;itc:0;sec:content-canvas" class="link " data-rapid_p="161" data-v9y="1"><b>Insider Monkey</b></a><b>.</b></p></div>  </div></div> <span class="article-footer yf-10hzt8r"><section class="privacy-container yf-19q4z23 inline" style="--privacy-link-font-weight: var(--font-normal);"><div class="terms-and-privacy small yf-19q4z23 column"><a class="subtle-link fin-size-small privacy-link-terms-link yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/terms?locale=en-US" data-rapid_p="162" data-v9y="1">Terms </a> and <a class="subtle-link fin-size-small privacy-link-privacy-link yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/privacy-policy?locale=en-US" data-rapid_p="163" data-v9y="1">Privacy Policy </a></div>  <div class="link-groups yf-19q4z23 column"> <a class="subtle-link fin-size-small privacy-link-dashboard noUnderline yf-1xqzjha" data-ylk="elm:corp;elmt:link;itc:0;sec:article;subsec:footer" href="https://guce.yahoo.com/privacy-dashboard?locale=en-US" data-rapid_p="164" data-v9y="1">Privacy Dashboard </a></div> <div class="link-groups yf-19q4z23 column">  <a href="/more-info" class="more-info yf-19q4z23" data-rapid_p="165">More Info</a></div></section></span></div>"""

    llm_query = """

        From https://finance.yahoo.com/news/, I have shared a sample of one news div.

        Please generate a JSON schema based only on the following properties:
        
        - title
        - date
        - full-article

        Only extract information related to the news article itself.  
        Do not include extra metadata, site-wide elements, or unrelated links.  
        Ensure the generated schema is clean, minimal, and strictly follows the required properties.
        Make sure to include the whole article text, not just part of it.

    """

    browser_config = BrowserConfig(
        headless=True,
        text_mode=True,
        light_mode=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        extractor = StructuredExtractor(
            crawler=crawler,
            extraction_strategy=JsonCssExtractionStrategy(
                JsonCssExtractionStrategy.generate_schema(
                    html=sample_html,
                    llm_config=LLMConfig(
                        provider="openai/gpt-4o-mini",
                    ),
                    query=llm_query,
                )
            )
        )

        extracted_data = await extractor.extract(urls=urls)
        print(json.dumps(extracted_data, indent=2))


if __name__ == "__main__":
    asyncio.run(usage_example())
