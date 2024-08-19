import os
import pandas as pd
from sapperrag.model.document import Document
from sapperrag.read.base import BaseReader, ReadResult
from sapperrag.read.read_tool import ReadToolFacTory
from uuid import uuid4
import asyncio


class DocumentReader(BaseReader):
    def __init__(self):
        super().__init__()

    def read(self, dir_path: str) -> ReadResult:
        """Synchronously reads all files in the given directory."""
        file_list = []
        file_reader = ReadToolFacTory()
        short_id = 0
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    # Use the FileReader to read the file content
                    row_content = file_reader.read_file(file_path)
                    doc_id = uuid4()
                    doc = Document(id=str(doc_id), raw_content=row_content, short_id=str(short_id), title=file_name)
                    short_id += 1
                    file_list.append(doc)
                except Exception as e:
                    print(f"Failed to read file {file_path}: {e}")

        return ReadResult(documents=file_list)

    async def aread(self, dir_path: str) -> ReadResult:
        """Asynchronously reads all files in the given directory."""
        # Use asyncio.to_thread to run the synchronous read method in a non-blocking way
        return await asyncio.to_thread(self.read, dir_path)
