from sapperrag import TextFileChunker
from sapperrag.embedding.base import BaseTextEmbedding
from sapperrag.index.base import Indexer
from sapperrag.llm.base import BaseLLM
from sapperrag.index.text.chunk_embedding import ChunkEmbedder


class TextIndexer(Indexer):
    def __init__(self, llm: BaseLLM, embeder: BaseTextEmbedding, local_file_reader):
        super().__init__()
        self.llm = llm
        self.embeder = embeder
        self.local_file_reader = local_file_reader

    def build_index(self, dir_path:str, **kwargs,):
        """Build the context for the local search mode."""
        read_result = self.local_file_reader.read(dir_path=dir_path)
        text_file_chunker = TextFileChunker(chunk_type="sliding")
        chunk_result = text_file_chunker.chunk(read_result.documents)
        chunk_embedder = ChunkEmbedder(self.embeder)
        embed_result = chunk_embedder.embed(chunk_result)
        chunk_embedder.save(dir_path)
        print("hello")
        return embed_result
