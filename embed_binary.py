"""
    Demo code for embedding binaries 
    once the model has been trained
"""
import argparse
import re
import time
import random
import numpy as np
from operator import itemgetter
from zipfile import ZipFile
from gensim.models import Word2Vec

from util_functions import get_file_names, generate_batch

def sort_files_by_size(zip_file, file_names):
    file_sizes = [x.file_size for x in zip_file.infolist()]
    fn, file_sizes = [list(x) for x in zip(*sorted(zip(file_names, file_sizes), key=itemgetter(1)))]
    return fn

def embed_batch(batch, max_size, embedding_dim, count_half_words):
    batch_size = len(batch)
    
    embedded_batch = np.zeros(shape=[batch_size, max_size, embedding_dim])

    for ba_idx, b in enumerate(batch):
        embedded_b = np.zeros(shape=[max_size, embedding_dim])
        for bdx, bword in enumerate(b):
            try:
                embedded_b[bdx] = w2v_model.wv[bword]
            except KeyError:
                count_half_words += 1
        embedded_batch[ba_idx] = embedded_b
    return embedded_batch, count_half_words

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract zip files')

    parser.add_argument('--zip_file_name', help='name of zip containing malware')
    parser.add_argument('--pass_string', help='password')
    parser.add_argument('--batch_size', default=4, 
                        help='number of binaries to add to model at a time')
    parser.add_argument('--existing_model', default=None, 
                        help='path of existing model')
    parser.add_argument('--token_size', default=2, 
                        help='Depends on how model was trained (byte, word, dword)')
    args = parser.parse_args()

    zip_file = ZipFile(args.zip_file_name, 'r')

    fn = get_file_names(zip_file)

    fn = sort_files_by_size(zip_file, fn)

    w2v_model = Word2Vec.load(args.existing_model)

    batch_size = int(args.batch_size)
    num_files = len(fn)
    print("Number of files: ", num_files)
    embedding_dim = len(w2v_model.wv['00e6'])
    print("Embedding dimensions:", embedding_dim)

    count_half_words = 0
    for idx in range(0, num_files, batch_size):
        st = time.time()

        batch = generate_batch(zip_file, fn, idx, batch_size, args.pass_string)

        max_size = max([len(x) for x in batch])

        embedded_batch, count_half_words = embed_batch(batch, max_size, embedding_dim, count_half_words)

        print("Number of incomplete byte words:", count_half_words)
        print("Batch Shape:", embedded_batch.shape)

        np.save('embedded_binaries/batch_{}.npy'.format(idx), embedded_batch)
        print('Time to embed:', round(time.time() - st, 3))
