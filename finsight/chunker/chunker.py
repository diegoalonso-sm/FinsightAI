from typing import List, Dict

from finsight.chunker.strategies.base import SplitterStrategy
from finsight.chunker.strategies.recursive import RecursiveSplitter


class TextChunker:

    """A generic text chunker that uses a pluggable splitting strategy. It can chunk single texts or a batch of documents while preserving metadata."""

    def __init__(self, splitter: SplitterStrategy):

        """
        Initialize a TextChunker instance.

        :param splitter: An instance of a text splitting strategy.
        :type splitter: SplitterStrategy

        """

        self.splitter = splitter

    def chunk_text(self, text: str) -> List[str]:

        """
        Split a single text into smaller chunks using the selected splitting strategy.

        :param text: Full text to split.
        :type text: str

        :return: A list of text chunks.
        :rtype: List[str]
        """

        return self.splitter.split_text(text)

    def chunk_documents(self, documents: List[Dict[str, str]], field: str = "content") -> List[Dict[str, str]]:

        """
        Split a batch of documents, preserving their metadata.

        Each chunk keeps the original document metadata and adds a 'chunk_index' and 'chunk' field.

        :param documents: A list of documents, each as a dictionary with a text field and metadata.
        :type documents: List[Dict[str, str]]

        :param field: The field name in the documents that contains the text to split.
        :type field: str

        :return: A list of chunked documents, each as a new dictionary.
        :rtype: List[Dict[str, str]]

        """

        chunked_documents = []

        for doc in documents:

            if field not in doc:
                raise ValueError(f"Field '{field}' not found in document: {doc}")

            chunks = self.chunk_text(doc[field])

            for i, chunk in enumerate(chunks):

                chunk = self.clean_text(chunk)
                chunked_documents.append({
                    **doc,
                    "chunk_index": i,
                    "chunk": chunk,
                })

                print(f"Chunk {i} for document '{doc.get('title', 'N/A')}' created.")
                print(f"Chunk content: {chunk[0:50]}...")  # Print first 100 characters for brevity

        return chunked_documents

    @staticmethod
    def clean_text(text: str) -> str:

        """
        Safely clean a text to remove problematic unicode characters.

        :param text: The text to clean.
        :type text: str

        :return: Cleaned text.
        :rtype: str

        """

        return text.encode('utf-8', 'ignore').decode('utf-8')


def usage_example():

    """
    Example usage of chunk_documents function with a dynamically selected splitter.

    This example:
    - Initializes a splitter using a factory method.
    - Splits a sample document into chunks.
    - Displays the resulting chunks.

    Requirements:
    - The splitter must be compatible with the TextChunker class.
    - The documents should contain the specified field for chunking.

    """

    documents = [
        {
            "title": "How Trump has wiped out the teams that protect student borrowers",
            "date": "2025-04-19 08:58:00",
            "full_article": "As it\u2019s torn through Washington\u2019s bureaucracy, the Trump administration has taken major steps to gut oversight of federal student loan servicers, raising questions about who will protect borrowers from errors by the massive government contractors that collect their monthly payments.This week, officials at the Consumer Financial Protection Bureau circulated a memo instructing staff to\u201cdeprioritize\u201dstudent loan matters at the watchdog agency, where they are trying to cut about 90% of the workforce. Since its creation in 2010, the CFPB has been the key regulator tasked with making sure loan servicers comply with federal consumer laws.At the Department of Education, meanwhile, mass layoffs have wiped out the Federal Student Aid office teams that were in charge of regularly checking loan servicers\u2019 work for mistakes and getting them fixed, multiple former officials told Yahoo Finance.The moves have left borrower advocates aghast, warning that former students will have far less recourse if servicers \u2014 who have long been a magnet for consumer complaints and have sometimes faced legal crackdowns for defrauding customers \u2014 mishandle their loans.\u201cIt means that the sorry state of the student loan system will only get worse \u2014 servicers can cut back on customer service, lose paperwork, and lie to borrowers knowing that no one is watching and they will never face justice,\u201d said Mike Pierce, executive director of the Student Borrower Protection Center, and former CFPB staffer during the Obama administration.Sign up for the Mind Your Money weekly newsletterSubscribeBy subscribing, you are agreeing to Yahoo'sTermsandPrivacy PolicyOne conservative education policy expert sympathetic to the administration\u2019s wider agenda also questioned some of the cuts.Jonathan Butcher, a senior research fellow at the conservative Heritage Foundation, said that while he supports President Trump\u2019s plans toend the Department of Educationand move student lending elsewhere in the government, eliminating its team responsible for overseeing servicers seems problematic, since it could lead to less accountability in the loan program.\u201cThey appear to have let go staff that are in a crucial spot,\u201d Butcher said, adding that he hoped there was a plan to fill their function going forward. Trump has said he intends to have the Small Business Administration take over student lending, but has not outlined any public plans for the transition, which some experts have argued would be illegal.Neither the Department of Education nor the CFPB responded to requests for comment.The problem with servicingDealing with servicers has long been a source of headaches for borrowers.In theory, the private companies and nonprofits that handle the work are supposed to both collect on the government\u2019s $1.6 trillion loan portfolio and help customers manage their debts effectively. But they\u2019ve earned a reputation for flubbing basic administrative tasks, like counting payments and cutting corners on customer service to save costs \u2014 sometimes leading tohours-long phone wait times. They have also frequently been criticized for failing to steer borrowers toward the most affordable payment plans, contributing to the staggering delinquency and default rates that have long plagued the student loan program.",
            "url": "https://finance.yahoo.com/news/how-trump-has-wiped-out-the-teams-that-protect-student-borrowers-173450503.html"
        },
        {
            "title": "How to think about earnings estimates during volatile times",
            "date": "2025-04-20 09:30:00",
            "full_article": "A version of this post first appeared on TKer.coEarnings estimates for the next 12 months are rising.And earnings estimates for 2025 and 2026 have been coming down.The above statements sound like they\u2019re in conflict. But they are actually twoways of communicatingthesame information. The differentiating factor: The passage of time.Calendar year vs. NTM earnings estimates \ud83d\udccaWe often hear analysts talk about earnings estimates based oncalendar years. For example, coming into this year Wall Street strategists presented theirestimates for 2025 earnings.As time passes and information emerges,analysts will adjust those estimates. Historically,analysts tendto graduallyrevise downthese calendar year estimates. And so far,this has been the case in 2025.However,time can pass quickly. And with calendar year estimates, what was once a discussion about future earnings can quickly become a discussion about past earnings.For example, at the beginning of the year, 2025 earnings represented the next-12 months\u2019 (NTM) earnings. But it\u2019s April now, which means any discussion of 2025 earnings involves an old quarter, and any discussion ofNTM earningsinvolves a quarter in 2026.Morgan Stanley\u2019s Michael Wilson shared a nice side-by-side visualization of this somewhat confusing dynamic. The chart on the left shows the S&P 500\u2019s NTM earnings per share (EPS). As time passes, you can see NTM EPS move up as it continuously incorporates the higher earnings expected in future periods.The chart on the right shows EPS estimates for 2025 and 2026 \u2014 static periods in time. As time passes, you can see how analysts\u2019 estimates have moved lower in recent months.NTM earnings estimates look good despite calendar year estimates coming down. (Source: Morgan Stanley)\"NTM EPS estimates continue to advance on the back of stronger 2026 EPS growth,\" Wilson observed. \"However, NTM EPS may show signs of flattening in recent weeks as 2025/2026 estimates revise slightly lower (-1%).\"To be clear, both charts employ the same analysts\u2019 estimates for earnings. They just differ in the way they reflect the effect of the passage of time.And the two charts are currently telling us that the promise of earnings growth on a rolling future basis is more than offsetting deteriorating expectations for static periods.This is importantin the context of valuation metricslike theforward price-earnings (P/E) ratio. If earnings are expected to grow, then forward earnings (E) will rise as time passes. This leads to downward pressure on P/E ratios.",
            "url": "https://finance.yahoo.com/news/how-to-think-about-earnings-estimates-during-volatile-times-133037581.html"
        }
    ]

    splitter = TextChunker(
        splitter=RecursiveSplitter(
            chunk_size=800,
            chunk_overlap=100,
        )
    )

    documents = splitter.chunk_documents(documents, field="full_article")

    for document in documents:

        print("=" * 80)
        print(f"Title: {document.get('title', 'N/A')}")
        print(f"Date: {document.get('date', 'N/A')}")
        print(f"Chunk Index: {document['chunk_index']}")
        print("-" * 80)
        print(document['chunk'])
        print("=" * 80)
        print("\n")


if __name__ == "__main__":
    usage_example()
