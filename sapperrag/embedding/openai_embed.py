from openai import OpenAI
import numpy as np
from typing import Any, List
from sapperrag.embedding.base import BaseTextEmbedding


class OpenAIEmbedding(BaseTextEmbedding):
    """Implementation of text embedding using OpenAI's API."""

    def __init__(self, openai_key: str, base_url: str, model_name: str):
        """
        Initializes the OpenAIEmbedding with a specific model.

        Args:
            model_name (str): The name of the OpenAI model to use for generating embeddings.
        """
        self.model_name = model_name
        self.client = OpenAI(api_key=openai_key, base_url=base_url)

    def embed(self, text: str, **kwargs: Any) -> List[float]:
        """
        Embed a text string synchronously.

        Args:
            text (str): The text to be embedded.

        Returns:
            List[float]: The embedding vector as a list of floats.
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name,
                **kwargs
            )
            embedding_vector = response.data[0].embedding
            return embedding_vector
        except Exception as e:
            print(f"Error while generating embedding: {e}")
            return []

    async def aembed(self, text: str, **kwargs: Any) -> List[float]:
        """
        Embed a text string asynchronously.

        Args:
            text (str): The text to be embedded.

        Returns:
            List[float]: The embedding vector as a list of floats.
        """
        try:
            response = await self.client.embeddings.acreate(
                input=text,
                model=self.model_name,
                **kwargs
            )
            embedding_vector = response.data[0].embedding
            return embedding_vector
        except Exception as e:
            print(f"Error while generating embedding: {e}")
            return []
