"""
    Demo code for training embeddings on byte code
"""
import argparse
import binascii
import re
import time
import random
from zipfile import ZipFile
from gensim.models import Word2Vec
from gensim.test.utils import common_texts, get_tmpfile


def get_file_names(zip_file_name):
    file_names = zip_file_name.namelist()
    return file_names


def load_file(zip_file, file_name, pass_string):
    file = zip_file.open(file_name, pwd=pass_string.encode('utf-8'))
    content = file.read()
    hex_string = binascii.hexlify(content)
    return hex_string


def split_string(hex_string):
    hex_len = len(hex_string)
    hex_chars = 2
    n_bytes = 2
    window = hex_chars * n_bytes
    byte_word_array = []
    for idx in range(0, hex_len, window):
        byte_word = hex_string[idx: idx+window].decode('utf-8')
        byte_word_array.append(byte_word)
    return byte_word_array


def train_model(b_words, model):
    if model:
        print("Updating model with {} files".format(len(b_words)))
        model.build_vocab(b_words, update=True)
    else:
        print("Training new model")
        model = Word2Vec(size=256, window=2, workers=8, sg=1, hs=0, negative=5)
        model.build_vocab(b_words)
    model.train(b_words, total_examples=len(b_words), epochs=15, compute_loss=True)
    return model

def generate_batch(zip_file, file_names, cur_idx, batch_size, password=None):
    batch = []
    print("Loading Batch")
    n_byte_words = 0
    for f in file_names[cur_idx:(cur_idx+batch_size)]:
        b_string = load_file(zip_file, f, password)
        b_words = split_string(b_string)
        batch.append(b_words)
        n_byte_words += len(b_words)
    print("Average number of byte words:", n_byte_words/float(batch_size))
    return batch


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract zip files')

    parser.add_argument('--zip_file_name', help='name of zip containing malware')
    parser.add_argument('--pass_string', help='password')
    parser.add_argument('--batch_size', default=4, 
                        help='number of binaries to add to model at a time')
    parser.add_argument('--existing_model', default=None, help='number of binaries to add to model at a time')
    args = parser.parse_args()

    zip_file = ZipFile(args.zip_file_name, 'r')

    fn = get_file_names(zip_file)

    random.shuffle(fn)

    if args.existing_model:
        w2v_model = Word2Vec.load(args.existing_model)
    else:
        w2v_model=None

    train_loss = 0

    batch_size = int(args.batch_size)
    num_files = len(fn)
    print("Number of files: ", num_files)
    for idx in range(0, num_files, batch_size):
        st = time.time()

        batch = generate_batch(zip_file, fn, idx, batch_size, args.pass_string)
        w2v_model = train_model(batch, w2v_model)
        print("Loss Change:", w2v_model.get_latest_training_loss() - train_loss)

        train_loss = w2v_model.get_latest_training_loss()
        print("Loss:", train_loss)

        t_delt = time.time() - st
        print('Elapsed Time:', round(t_delt, 3))

        remaining_batches = (num_files - idx + batch_size) / batch_size
        print('Estimated Time Remaining (hrs):', round(t_delt * remaining_batches / 3600))

        if idx > 0 and idx % (batch_size * 10) == 0:
            print("Saving model")
            w2v_model.save("arthropod.model")
    w2v_model.save("arthropod.model")
