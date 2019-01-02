"""
	Tests for util_functions.py
"""
from zipfile import ZipFile

from util_functions import get_file_names
from util_functions import load_file
from util_functions import split_string
from util_functions import generate_batch

TEST_ZIP = 'tests/test_data.zip'
TEST_ZIP_FILE = ZipFile(TEST_ZIP, 'r')


def test_get_file_names():
	"""
		Test if all file names are present
	"""
	fn = get_file_names(TEST_ZIP_FILE)
	assert len(fn) == 4
	assert fn[0] == 'abcdefg'


def test_load_file():
	"""
		Tests if it loads binary and converts to hex
		correctly
	"""
	hex_string = load_file(TEST_ZIP_FILE, 'wxyz')
	assert hex_string == b'7778797a'


def test_split_string():
	"""
		Tests if splits hex string into 
		regular strings of byte words
	"""
	hex_string = b'7778797a'
	byte_word_array = split_string(hex_string)
	assert byte_word_array == ['7778', '797a']


def test_generate_batch():
	"""
		Tests if it generates a batch correctly
	"""
	fn = get_file_names(TEST_ZIP_FILE)
	current_index = 1
	batch_size = 2
	batch = generate_batch(TEST_ZIP_FILE, fn, current_index, batch_size, password=None)
	assert len(batch) == batch_size
	assert batch[0][0] == '6869'
