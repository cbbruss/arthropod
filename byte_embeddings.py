"""
    Demo code for training embeddings on byte code
"""
import argparse
import time
from typing import List
from gensim.models import Word2Vec

from util_functions import ZipDataHandler


def train_model(
    b_words: List[List[str]],
    model: Word2Vec = None
) -> Word2Vec:
    """
        If a model already exists update it with a new batch of data
        otherwise train a brand new model

        Args:
            b_words: list of lists of byte_words
            model (optional): existing word2vec model

        Returns:
            model: word2vec model

    """
    if model:
        print("Updating model with {} files".format(len(b_words)))
        model.build_vocab(b_words, update=True)
    else:
        print("Training new model")
        model = Word2Vec(size=256, window=2,
                         workers=8, sg=1, hs=0,
                         negative=5, min_count=0)
        model.build_vocab(b_words)
    model.train(b_words, total_examples=len(b_words),
                epochs=15, compute_loss=True)
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract zip files')

    parser.add_argument('--zip_file_name',
                        help='name of zip containing malware')
    parser.add_argument('--pass_string', help='password')
    parser.add_argument('--batch_size', default=4,
                        help='number of binaries to add to model at a time')
    parser.add_argument('--existing_model',
                        default=None,
                        help='number of binaries to add to model at a time')
    args = parser.parse_args()

    zdh = ZipDataHandler(args.zip_file_name, password=args.pass_string)

    zdh.shuffle_file_names()

    if args.existing_model:
        w2v_model = Word2Vec.load(args.existing_model)
    else:
        w2v_model = None

    train_loss = 0

    batch_size = int(args.batch_size)
    num_files = zdh.num_files
    print("Number of files: ", num_files)
    for idx in range(0, num_files, batch_size):
        st = time.time()

        batch = zdh.generate_batch(idx, batch_size)
        w2v_model = train_model(batch, w2v_model)
        change = w2v_model.get_latest_training_loss() - train_loss
        print("Loss Change:", change)

        train_loss = w2v_model.get_latest_training_loss()
        print("Loss:", train_loss)

        t_delt = time.time() - st
        print('Elapsed Time:', round(t_delt, 3))

        remaining_batches = (num_files - idx + batch_size) / batch_size
        rt = round(t_delt * remaining_batches / 3600)
        print('Estimated Time Remaining (hrs):', rt)

        if idx > 0 and idx % (batch_size * 10) == 0:
            print("Saving model")
            w2v_model.save("arthropod.model")
    w2v_model.save("arthropod.model")
