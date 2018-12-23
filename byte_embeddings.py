"""
    Demo code for training embeddings on byte code
"""
import argparse
import binascii
import re
from zipfile import ZipFile
from gensim.models import Word2Vec
from gensim.test.utils import common_texts, get_tmpfile


def get_file_names(zip_file_name):
    with ZipFile(zip_file_name, 'r') as zip:
        file_names = zip.namelist()
    return file_names


def load_file(zip_file_name, file_name, pass_string):
    with ZipFile(zip_file_name, 'r') as zip:
        file = zip.open(file_name, pwd=pass_string.encode('utf-8'))
        content = file.read()
        hex_string = binascii.hexlify(content)
    return split_string(hex_string)


def split_string(hex_string):
    hex_len = len(hex_string)
    n_bytes = int(hex_len / 2)
    c = 0
    byte_word_array = []
    for idx in range(n_bytes-1):
        st = idx*2 + c
        stop = st + 4
        byte_word_array.append(hex_string[st: stop].decode('utf-8'))
    return byte_word_array


def train_model(b_words, model):
    if model:
        print("Updating model")
        model.train(b_words, total_examples=len(b_words), epochs=2)
    else:
        print("Training new model")
        model = Word2Vec(b_words, size=8, window=8, workers=8, sg=1, hs=1, negative=5)
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract zip files')

    parser.add_argument('--zip_file_name', help='name of zip containing malware')
    parser.add_argument('--pass_string', help='password')
    parser.add_argument('--batch_size', default=4, 
                        help='number of binaries to add to model at a time')
    parser.add_argument('--existing_model', default=None, help='number of binaries to add to model at a time')
    args = parser.parse_args()

    fn = get_file_names(args.zip_file_name)

    if args.existing_model:
        w2v_model = Word2Vec.load(args.existing_model)
    else:
        w2v_model=None

    batch_size = args.batch_size
    batch = []
    for idx in range(0, len(fn), batch_size):
        for f in fn[idx:idx+batch_size]:
            print('opening: ', f)
            b_words = load_file(args.zip_file_name, f, args.pass_string)
            batch.append(b_words)
        w2v_model = train_model(batch, w2v_model)
        print(w2v_model.wv['4d5a'])
    w2v_model.save("arthropod.model")
