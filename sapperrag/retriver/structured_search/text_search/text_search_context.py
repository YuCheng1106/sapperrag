from __future__ import annotations

from typing import Any, Optional, List
import pandas as pd
import tiktoken
from ....retriver.context_builder.builders import TextContextBuilder
from ....retriver.structured_search.text_search.query_embedding import map_query_to_text_chunks
from ....retriver.context_builder.text_context import build_text_context
from sapperrag.model import load_text_chunks, load_embeddings, TextChunk
import os


class TextSearchContext(TextContextBuilder):
    def __init__(self,
                 dir_path: Optional[str] = None,
                 text_embedder: Any = None,
                 chunk_data: List[TextChunk] = [],
                 vector_db: Optional[Any] = None):
        """
        Initialize the TextSearchContext with either a directory path or directly with chunk_data and vector_db.

        Parameters:
            dir_path (Optional[str]): Directory path containing the data files. Either this or chunk_data/vector_db must be provided.
            text_embedder (Any): The embedder used for generating text embeddings.
            chunk_data (Optional[pd.DataFrame]): Direct input of chunk data as a DataFrame. Optional if dir_path is provided.
            vector_db (Optional[Any]): Direct input of the vector database. Optional if dir_path is provided.
        """
        # Load data from files if a directory path is provided
        if dir_path:
            self.text_chunks = load_text_chunks(os.path.join(dir_path, "text_chunks.csv"))
            self.vector_db = load_embeddings(os.path.join(dir_path, "text_vector_db.npy.npz"))
        else:
            # Use directly provided data if available
            if chunk_data is None or vector_db is None:
                raise ValueError("Either 'dir_path' or both 'chunk_data' and 'vector_db' must be provided.")
            self.text_chunks = chunk_data
            self.vector_db = vector_db

        self.text_embedder = text_embedder

    def build_context(self, query: str, **kwargs: Any) -> Any:
        """Build the context for the local search mode."""
        # Use the token encoder for text processing
        token_encoder = tiktoken.get_encoding("cl100k_base")

        # Map the query to relevant text chunks using the provided embedder and vector database
        sorted_chunks = map_query_to_text_chunks(query, self.text_chunks, self.vector_db, self.text_embedder)

        final_context = list[str]()
        final_context_data = dict[str, pd.DataFrame]()

        # Build the text context from the sorted chunks
        text_context, text_context_data = build_text_context(sorted_chunks, token_encoder)

        if text_context.strip() != "":
            final_context.append(str(text_context))
            final_context_data["Text"] = text_context_data

        return "\n\n".join(final_context), final_context_data
