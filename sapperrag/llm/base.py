from abc import ABC, abstractmethod
from typing import Any


class BaseLLM(ABC):
    """The Base LLM implementation."""

    @abstractmethod
    def generate(
        self,
        messages,
        streaming: bool = False,
        **kwargs: Any,
    ) -> str:
        """Generate a response."""

    @abstractmethod
    async def agenerate(
        self,
        messages,
        streaming: bool = False,
        **kwargs: Any,
    ) -> str:
        """Generate a response asynchronously."""
