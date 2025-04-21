from abc import ABC, abstractmethod
from typing import List


class SplitterStrategy(ABC):

    """Abstract base class for text splitting strategies."""

    @abstractmethod
    def split_text(self, text: str) -> List[str]:

        """
        Split a given text into smaller chunks.

        :param text: Full text to split.
        :return: List of text chunks.
        """

        pass