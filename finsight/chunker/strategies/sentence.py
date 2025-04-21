from typing import List

import nltk
from nltk.tokenize import sent_tokenize

from finsight.chunker.strategies.base import SplitterStrategy


class SentenceSplitter(SplitterStrategy):

    """
    Splitting strategy that divides text into individual sentences using the NLTK library.

    This splitter is suitable for tasks where highly granular sentence-level chunks are preferred,
    such as fine-grained question answering (QA), sentence-level classification, or dense passage retrieval.

    It does not enforce a maximum number of characters per chunk.

    """

    def __init__(self):

        try:
            nltk_folder = nltk.data.find("tokenizers/punkt")
            print(f"NLTK punkt tokenizer found at: {nltk_folder}")

        except LookupError:
            nltk.download("punkt_tab")

    def split_text(self, text: str) -> List[str]:

        """
        Split the given text into sentences using NLTK's pretrained sentence tokenizer.

        :param text:The full text to split into sentences. It should be well-formed (punctuated) for optimal sentence boundary detection.
        :type text: str

        :return: A list of sentences extracted from the original text.
        :rtype: List[str]

        """

        return sent_tokenize(text)


def usage_example():

    """
    Example usage of the SentenceSplitter class.

    This example:
    - Initializes the SentenceSplitter.
    - Splits a sample text into sentences.
    - Displays the resulting sentences.

    Requirements:
    - NLTK library must be installed.

    """

    text = (
        "The financial markets had a volatile day. "
        "Analysts predict that the trend might continue into the next quarter. "
        "However, some investors remain optimistic."
    )

    splitter = SentenceSplitter()
    sentences = splitter.split_text(text)

    for i, sentence in enumerate(sentences):
        print(f"Sentence {i + 1}: {sentence}")


if __name__ == "__main__":
    usage_example()
