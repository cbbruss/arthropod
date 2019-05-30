"""
    Utils
"""
import binascii
import random
from zipfile import ZipFile
from typing import List
from operator import itemgetter


class ZipDataHandler():

    def __init__(
        self,
        zip_file_name: str,
        password: str = None
    ):
        """
            Initialize class with zip file name and
            password if available
        """
        self.zip_file = ZipFile(zip_file_name, 'r')
        self.zip_file_names = self.zip_file.namelist()
        self.num_files = len(self.zip_file_names)
        if password:
            self.password = password.encode('utf-8')
        else:
            self.password = None

    def shuffle_file_names(self):
        """
            Shuffles the order of file names
        """
        random.shuffle(self.zip_file_names)
        print("Shuffled file order")

    def generate_batch(
        self,
        cur_idx: int,
        batch_size: int,
    ) -> List[List[str]]:
        """ Given a list of files generates a batch starting at
        the index provided of size provided

        Args:
            cur_idx: Current location in file names
            batch_size: number of files to include in batch

        Returns:
            batch: list of lists containing hex byte words
        """
        batch = []
        print("Loading Batch")
        n_byte_words = 0
        end_idx = cur_idx + batch_size
        batch_fn = self.zip_file_names[cur_idx:end_idx]
        for f in batch_fn:
            b_string = self._load_file(f)
            b_words = self._split_string(b_string)
            batch.append(b_words)
            n_byte_words += len(b_words)
        average_byte_words = n_byte_words / float(batch_size)
        print("Average number of byte words:", average_byte_words)
        return batch, batch_fn

    def sort_files_by_size(self):
        """
            Sorts all the file names according to the size
            of the corresponding files
        """
        info = self.zip_file.infolist()
        names = self.zip_file.namelist()
        file_sizes = [x.file_size for x in info]
        zip_fn_fs = zip(names, file_sizes)
        zipped_files = zip(*sorted(zip_fn_fs, key=itemgetter(1)))
        fn, file_sizes = [list(x) for x in zipped_files]
        self.zip_file_names = fn

    def _load_file(
        self,
        file_name: str
    ) -> bytes:
        """ Opens a single file and returns
        a hexadecimal version of that file

        Args:
            file_name: name of file inside ZipFile object
        Returns:
            hex_string: hexadecimal string of file
        """
        file = self.zip_file.open(file_name, pwd=self.password)
        content = file.read()
        hex_string = binascii.hexlify(content)
        return hex_string

    def _split_string(
        self,
        hex_string: bytes
    ) -> List[str]:
        """ Given a byte string of hexadecimal values
        returns an array containing all the byte words
        starting at index 0. A byte is two hex characters
        and a byte word is two bytes therefor each byteword
        contains 4 hex characters.

        Args:
            hex_string: byte string of hexadecimals

        Returns:
            byte_word_array: list of byte words in the binary
        """
        hex_len = len(hex_string)
        hex_chars = 2
        n_bytes = 2
        window = hex_chars * n_bytes
        byte_word_array = []
        for idx in range(0, hex_len, window):
            byte_word = hex_string[idx: idx + window].decode('utf-8')
            byte_word_array.append(byte_word)
        return byte_word_array
