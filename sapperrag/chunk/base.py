from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
from sapperrag.model.text_chunk import TextChunk


class BaseChunker(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def chunk(self, dir_path: str) -> List[TextChunk]:
        """Synchronously searches for files in the directory and returns a list of TextChunk objects."""
        pass

    @abstractmethod
    async def achunk(self, dir_path: str) -> List[TextChunk]:
        """Asynchronously searches for files in the directory and returns a list of TextChunk objects."""
        pass

    @abstractmethod
    async def save(self, save_path: str):
        """Asynchronously searches for files in the directory and returns a list of TextChunk objects."""
        pass
