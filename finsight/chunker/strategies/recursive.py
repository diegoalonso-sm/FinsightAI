from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from finsight.chunker.strategies.base import SplitterStrategy


class RecursiveSplitter(SplitterStrategy):

    """
    Splitting strategy that recursively divides text into smaller chunks based on
    paragraphs, sentences, spaces, and characters.

    This splitter is suitable for structured texts like articles, reports, or essays,
    preserving natural language boundaries.

    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):

        """
        Initialize a RecursiveSplitter instance.

        :param chunk_size:
            The maximum number of characters allowed in each chunk.
            The splitter will try to keep each fragment below this limit
            while respecting natural text boundaries such as paragraphs, sentences, and words.
            If a clean cut is not possible, the splitter falls back to character-based splitting.

        :type chunk_size: int

        :param chunk_overlap:
            The number of characters to overlap between consecutive chunks.
            Overlapping ensures that important context from the end of one chunk
            is preserved at the beginning of the next chunk,
            which improves performance in semantic search and retrieval tasks.

        :type chunk_overlap: int

        """

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_text(self, text: str) -> List[str]:

        """
        Split the given text into smaller chunks according to the recursive splitting rules.

        :param text: The full text to split.
        :type text: str

        :return: A list of text chunks.
        :rtype: List[str]

        """

        return self.splitter.split_text(text)


def usage_example():

    """
    Example usage of the RecursiveSplitter class.

    This example:
    - Creates an instance of RecursiveSplitter.
    - Splits a sample text into chunks.
    - Prints each chunk with its index.

    """

    text = "This is a sample text. It contains multiple sentences. Let's see how it splits!"

    splitter = RecursiveSplitter(chunk_size=40, chunk_overlap=20)
    chunks = splitter.split_text(text)

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {chunk}")


if __name__ == "__main__":
    usage_example()
