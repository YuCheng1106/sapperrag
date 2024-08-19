import asyncio
import re
import markdown
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter
import string
from abc import ABC, abstractmethod
from sapperrag.chunk.base import BaseChunker, TextChunk
from typing import List
import nltk as nl

# Abstract base class for chunking strategies
class BaseChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass


class ChunkToolFacTory:
    def __init__(self):
        self.strategies = {
            "regex": RegexChunking(),
            "markdown": MarkdownChunking(),
            "fixed": FixedLengthWordChunking(),
            "sliding": SlidingWindowChunking(),
            # Add more strategies as needed
        }

    def chunk_file(self, file_path: str, strategy_name: str) -> List[str]:
        strategy = self.strategies.get(strategy_name)
        if strategy is None:
            raise ValueError(f"Strategy {strategy_name} is not supported.")

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        return strategy.chunk(content)


# Regex-based chunking
class RegexChunking(BaseChunkingStrategy):
    def __init__(self, patterns=None):
        if patterns is None:
            patterns = [r'\n\n']  # Default split pattern
        self.patterns = patterns

    def chunk(self, text: str) -> List[str]:
        paragraphs = [text]
        for pattern in self.patterns:
            new_paragraphs = []
            for paragraph in paragraphs:
                new_paragraphs.extend(re.split(pattern, paragraph))
            paragraphs = new_paragraphs
        return paragraphs


# Markdown chunking
class MarkdownChunking(BaseChunkingStrategy):
    def __init__(self, patterns=None):
        if patterns is None:
            patterns = [r'\n\n']
        self.patterns = patterns

    def chunk(self, text: str) -> List[str]:
        # Convert Markdown text to HTML
        html = markdown.markdown(text)
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # Extract all paragraphs
        paragraphs = soup.find_all('p')
        # Return text of all paragraphs
        return [para.text for para in paragraphs]


# Fixed-length word chunks
class FixedLengthWordChunking(BaseChunkingStrategy):
    def __init__(self, chunk_size=100):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> List[str]:
        words = text.split()
        return [' '.join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]


# Sliding window chunking
class SlidingWindowChunking(BaseChunkingStrategy):
    def __init__(self, window_size=100, step=50):
        self.window_size = window_size
        self.step = step

    def chunk(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.step):
            chunks.append(' '.join(words[i:i + self.window_size]))
        return chunks
