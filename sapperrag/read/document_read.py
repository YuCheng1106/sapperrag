import os
import pandas as pd
from typing import List
from sapperrag.model.document import Document
from sapperrag.read.base import BaseReader, ReadResult
from sapperrag.read.read_tool import ReadToolFacTory
from sapperrag.model import save_model_to_csv
from uuid import uuid4
import asyncio


class DocumentReader(BaseReader):
    def __init__(self):
        super().__init__()
        self.result: List[Document] = []

    def read(self, dir_path: str) -> List[Document]:
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
        self.result = file_list
        return file_list

    async def aread(self, dir_path: str) -> List[Document]:
        """Asynchronously reads all files in the given directory."""
        # Use asyncio.to_thread to run the synchronous read method in a non-blocking way
        return await asyncio.to_thread(self.read, dir_path)

    def save(self, save_path: str):
        save_model_to_csv(self.result, os.path.join(save_path, "document.csv"))
