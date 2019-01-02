"""
	Utils
"""
import binascii

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