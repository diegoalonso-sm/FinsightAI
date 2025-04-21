from typing import List

from langchain_text_splitters import TokenTextSplitter

from finsight.chunker.strategies.base import SplitterStrategy


class TokenSplitter(SplitterStrategy):

    """
    Splitting strategy that divides text into chunks based on token count instead of character count.

    This splitter is useful when working with systems where token-based limitations exist,
    such as language models (e.g., OpenAI GPT models) that charge or limit based on tokens rather than characters.

    :param chunk_size: Maximum number of tokens allowed per chunk. Defaults to 256.
    :type chunk_size: int

    :param chunk_overlap: Number of overlapping tokens between consecutive chunks to preserve context. Defaults to 50.
    :type chunk_overlap: int

    """

    def __init__(self, chunk_size: int = 256, chunk_overlap: int = 50):

        """
        Initialize a TokenSplitter instance.

        :param chunk_size: Maximum tokens per chunk.
        :type chunk_size: int

        :param chunk_overlap: Overlapping tokens between chunks.
        :type chunk_overlap: int

        """

        self.splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_text(self, text: str) -> List[str]:

        """
        Split the provided text into chunks based on token limits.

        :param text: The full text to split into token-based chunks.
        :type text: str

        :return: A list of text chunks, each within the specified token limits.
        :rtype: List[str]

        """

        return self.splitter.split_text(text)


def usage_example():

    """
    Example usage of the TokenSplitter class.

    This example:
    - Initializes the TokenSplitter.
    - Splits a sample text into token-based chunks.
    - Displays the resulting chunks.

    Requirements:
    - langchain_text_splitters library must be installed.
    - TokenTextSplitter from langchain_text_splitters must be available.
    - The text should be well-formed to ensure optimal tokenization.

    """

    text = (
        "Natural Language Processing (NLP) has seen significant advances "
        "in recent years. Transformers have revolutionized how we approach tasks "
        "such as translation, summarization, and question answering."
    )

    splitter = TokenSplitter(chunk_size=30, chunk_overlap=5)
    chunks = splitter.split_text(text)

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}: {chunk}\n")


if __name__ == "__main__":
    usage_example()
