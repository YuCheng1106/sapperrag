from typing import Any, List
import torch
import os
import asyncio

from sapperrag.embedding.base import BaseTextEmbedding


class LocalModelEmbedding(BaseTextEmbedding):
    """Implementation of text embedding using a local BERT model."""

    def __init__(self, path: str):
        from transformers import BertModel, BertTokenizer, BertConfig
        """
        Initialize the embedding model by loading a pre-trained BERT model and tokenizer.

        Args:
            path (str): Path to the directory containing model weights, config, and vocabulary.
        """
        # Paths to model files
        model_path = os.path.join(path, 'pytorch_model.bin')
        config_path = os.path.join(path, 'config.json')
        vocab_path = os.path.join(path, 'vocab.txt')

        # Load model configuration
        config = BertConfig.from_pretrained(config_path)

        # Initialize model and tokenizer
        self.model = BertModel(config)
        self.tokenizer = BertTokenizer(vocab_file=vocab_path)

        # Load model weights asynchronously
        asyncio.run(self._load_model_weights(model_path))

    async def _load_model_weights(self, model_path: str):
        """
        Asynchronously load the model weights.

        Args:
            model_path (str): Path to the model weights file.
        """
        # Load state_dict asynchronously
        state_dict = await self._load_file_async(model_path)
        self.model.load_state_dict(state_dict)

    async def _load_file_async(self, file_path: str) -> dict:
        """
        Asynchronously load a file.

        Args:
            file_path (str): Path to the file to be loaded.

        Returns:
            dict: Loaded file content.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: torch.load(file_path))

    def embed(self, text: str, **kwargs: Any) -> List[float]:
        """
        Embed a text string synchronously.

        Args:
            text (str): The text to be embedded.

        Returns:
            List[float]: The embedding vector as a list of floats.
        """
        try:
            # Tokenize input text
            inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)

            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Get [CLS] token vector
            cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()

            return cls_embedding.flatten().tolist()
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
            # Tokenize input text
            inputs = self.tokenizer(text, return_tensors='pt')

            # Generate embeddings asynchronously
            loop = asyncio.get_event_loop()
            embedding_vector = await loop.run_in_executor(None, self._generate_embedding, inputs)

            return embedding_vector
        except Exception as e:
            print(f"Error while generating embedding: {e}")
            return []

    def _generate_embedding(self, inputs) -> List[float]:
        """
        Generate embedding vector synchronously.

        Args:
            inputs: Tokenized inputs for the model.

        Returns:
            List[float]: The embedding vector as a list of floats.
        """
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get [CLS] token vector
        cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()

        return cls_embedding.flatten().tolist()
