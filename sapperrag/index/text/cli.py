from sapperrag.index.base import Indexer


class TextIndexer(Indexer):
    """Base class for local-search context builders."""

    def build_index(
            self,
            **kwargs,
    ):
        """Build the context for the local search mode."""
