from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd
from sapperrag.model import Document


@dataclass
class ReadResult:
    documents: list[Document]


class BaseConversionStrategy(ABC):
    @abstractmethod
    def convert(self, file_path: str) -> Document:
        pass


class BaseReader(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def read(self, dir_path: str) -> list[Document]:
        """Searches for files that match the query and returns a list of ReadResult objects."""
        pass

    @abstractmethod
    async def aread(self, dir_path: str) -> list[Document]:
        """Asynchronously searches for files that match the query and returns a list of ReadResult objects."""
        pass

    @abstractmethod
    async def save(self, save_path: str):
        """Asynchronously searches for files that match the query and returns a list of ReadResult objects."""
        pass
