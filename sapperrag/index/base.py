from abc import ABC, abstractmethod

import pandas as pd


class Indexer(ABC):
    """Base class for global-search context builders."""

    @abstractmethod
    def build_index(
        self, **kwargs
    ):
        """Build the context for the global search mode."""

