from abc import ABC, abstractmethod
from typing import Any, List
from sapperrag.llm.base import BaseLLM


class BaseSearch(ABC):
    """The Base Search implementation."""

    def __init__(self, context_builder, llm: BaseLLM):
        self.context_builder = context_builder
        self.llm = llm

    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> List[Any]:
        """Search for the given query.

        Args:
            query (str): The search query.
            **kwargs (Any): Additional keyword arguments for the search.

        Returns:
            List[Any]: The search results.
        """

    @abstractmethod
    async def asearch(self, query: str, **kwargs: Any) -> List[Any]:
        """Asynchronously search for the given query.

        Args:
            query (str): The search query.
            **kwargs (Any): Additional keyword arguments for the search.

        Returns:
            List[Any]: The search results.
        """
