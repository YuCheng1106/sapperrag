from abc import ABC, abstractmethod
from typing import Any


class BaseTextEmbedding(ABC):
    """The text embedding interface."""

    @abstractmethod
    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Embed a text string."""

    @abstractmethod
    async def aembed(self, text: str, **kwargs: Any) -> list[float]:
        """Embed a text string asynchronously."""
