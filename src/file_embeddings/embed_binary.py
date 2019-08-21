"""
    Demo code for embedding binaries
    once the model has been trained
"""
import argparse
import time
from typing import List, Tuple
import numpy as np
from gensim.models import Word2Vec

from util_functions import ZipDataHandler


def embed_batch(
    model: Word2Vec,
    batch: List[List[str]],
    max_size: int,
    embedding_dim: int,
    count_half_words: int
) -> Tuple[np.ndarray, int]:
    """
        Given a batch of tokenized binaries return an numpy array
        of embedded values

        Args:
            batch: tokenized binaries in hex
            max_size: maximum len of binaries in batch
            embedding_dim: dimensions of embedding model
            count_half_words: running count of words not in model

        Returns:
            embedded_batch: np array [batch_size, max_size, embedding_dim]
            count_half_words: running count of words not in model
    """
    batch_size = len(batch)

    embedded_batch = np.zeros(shape=[batch_size, max_size, embedding_dim])

    for ba_idx, b in enumerate(batch):
        embedded_b = np.zeros(shape=[max_size, embedding_dim])
        for bdx, bword in enumerate(b):
            try:
                embedded_b[bdx] = model.wv[bword]
            except KeyError:
                count_half_words += 1
        embedded_batch[ba_idx] = embedded_b
    return embedded_batch, count_half_words


def average_batch(embedded_batch: np.ndarray) -> np.ndarray:
    """
        Given a batch of files that have each byteword embedded
        in a dense vector, collapse the entire file by
        averaging over all vectors and also computing the
        standard deviation of the vectors along each dimension.

        Args:
            embedded_batch: np array [batch_size, max_size, embedding_dim]

        Returns:
            batch_params: np array [batch, embedding_dim, 2]

    """
    batch_average = np.mean(embedded_batch, axis=1)
    batch_average = np.expand_dims(batch_average, axis=2)
    batch_std = np.std(embedded_batch, axis=1)
    batch_std = np.expand_dims(batch_std, axis=2)
    batch_params = np.concatenate([batch_average, batch_std], axis=2)
    return batch_params


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract zip files')

    parser.add_argument('--zip_file_name',
                        help='name of zip containing malware')
    parser.add_argument('--pass_string', help='password')
    parser.add_argument('--batch_size', default=4,
                        help='number of binaries to add to model at a time')
    parser.add_argument('--existing_model', help='path of existing model')
    args = parser.parse_args()

    zdh = ZipDataHandler(args.zip_file_name, password=args.pass_string)

    zdh.sort_files_by_size()

    w2v_model = Word2Vec.load(args.existing_model)

    batch_size = int(args.batch_size)
    num_files = zdh.num_files
    print("Number of files: ", num_files)
    embedding_dim = w2v_model.vector_size
    print("Embedding dimensions:", embedding_dim)

    count_half_words = 0
    for idx in range(0, num_files, batch_size):
        st = time.time()

        batch, batch_fn = zdh.generate_batch(idx, batch_size)

        max_size = max([len(x) for x in batch])

        embedded_batch, count_half_words = embed_batch(w2v_model,
                                                       batch,
                                                       max_size,
                                                       embedding_dim,
                                                       count_half_words)

        print("Number of incomplete byte words:", count_half_words)
        print("Batch Shape:", embedded_batch.shape)

        batch_params = average_batch(embedded_batch)
        np.save('embedded_binaries/batch_p_{}.npy'.format(idx), batch_params)
        fn_file = "embedded_binaries/batch_p_{}_fns.txt".format(idx)
        open(fn_file, "w").write('\n'.join(batch_fn))

        print('Time to embed:', round(time.time() - st, 3))
