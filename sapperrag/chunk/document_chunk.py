import os
from sapperrag.chunk.base import BaseChunker
from sapperrag.model.document import Document
from sapperrag.model.text_chunk import TextChunk
from sapperrag.chunk.chunk_tool import ChunkToolFacTory
from sapperrag.model import save_model_to_csv
from uuid import uuid4
from typing import List
import asyncio


class TextFileChunker(BaseChunker):
    def __init__(self, chunk_type: str = "sliding", **kwargs):
        super().__init__()
        self.chunker = ChunkToolFacTory().strategies.get(chunk_type)
        if not self.chunker:
            raise ValueError(f"Strategy {chunk_type} is not supported.")
        self.result: List[TextChunk] = []

    def chunk(self, documents: List[Document]) -> List[TextChunk]:
        """Chunks the text based on the selected strategy."""
        all_chunks = []
        short_id = 0
        for document in documents:
            try:
                chunks = self.chunker.chunk(document.raw_content)  # Assuming raw_content contains the text data
                for chunk in chunks:
                    text_chunk = TextChunk(
                        id=str(uuid4()),  # Generate a unique ID for each chunk
                        text=chunk,  # Assign the chunked text
                        document_ids=[document.id],  # Link the chunk to its source document
                        short_id=str(short_id)
                    )
                    all_chunks.append(text_chunk)
                    short_id += 1
            except Exception as e:
                print(f"Error chunking document {document.title}: {e}")

        self.result = all_chunks
        return all_chunks

    async def achunk(self, documents: List[Document]) -> List[TextChunk]:
        """Asynchronously chunks the text based on the selected strategy."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.chunk, documents)

    def save(self, save_path: str):
        save_model_to_csv(self.result, os.path.join(save_path, "text_chunks.csv"))
