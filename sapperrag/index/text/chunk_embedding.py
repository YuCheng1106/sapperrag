import os
import numpy as np
import concurrent.futures

import pandas as pd

from sapperrag.model.text_chunk import TextChunk
from typing import List


class ChunkEmbedder:
    def __init__(self, text_embeder):
        self.text_embeder = text_embeder
        self.chunks = []

    def embed_chunks(self, text):
        response = self.text_embeder.embed(text)
        attribute_vector = np.array(response)
        return attribute_vector

    def embed(self, chunks: List[TextChunk]):
        def process_row(row):
            vector = self.embed_chunks(row.text)
            return vector

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_row, row): idx for idx, row in enumerate(chunks)}

            for future in concurrent.futures.as_completed(futures):
                idx = futures[future]
                try:
                    attribute_vector = future.result()
                    chunks[idx].text_embedding = attribute_vector
                except Exception as e:
                    print(f"Error processing row {idx}: {e}")

        self.chunks = chunks
        return chunks

    def save(self, dir_path):
        output_file = os.path.join(dir_path, "text_vector_db.npy")

        # Prepare the data for saving
        ids = [chunk.id for chunk in self.chunks]
        embeddings = np.array([chunk.text_embedding for chunk in self.chunks])

        # Save the data
        np.savez_compressed(output_file, ids=ids, embeddings=embeddings)


    def load_embeddings_to_dataframe(self, file_path):
        # Load the data from the .npz file
        with np.load(file_path, allow_pickle=True) as data:
            ids = data['ids']
            embeddings = data['embeddings']

            # Convert byte IDs to string if necessary
            ids = [id.decode('utf-8') if isinstance(id, bytes) else id for id in ids]

            # Create a DataFrame
            df = pd.DataFrame({
                'ID': ids,
                'Embedding': list(embeddings)
            })

            return df
