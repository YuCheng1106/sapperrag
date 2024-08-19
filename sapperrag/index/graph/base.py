from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List
from sapperrag.llm.base import BaseLLM
from sapperrag.model.text_chunk import TextChunk


@dataclass
class ConstructResult:
    schema: []
    definition: {}


class BaseConstructor(ABC):
    def __init__(self, text_chunks: list[TextChunk], llm: BaseLLM):
        self.text_chunks = text_chunks
        self.llm = llm

    @abstractmethod
    def construct(self, aim="extract knowledge", info=None) -> ConstructResult:
        """Synchronously searches for files in the directory and returns a list of TextChunk objects."""
        if info is None:
            info = {}
        pass

    @abstractmethod
    async def aconstruct(self, aim="extract knowledge", info=None) -> ConstructResult:
        """Asynchronously searches for files in the directory and returns a list of TextChunk objects."""
        if info is None:
            info = {}
        pass
