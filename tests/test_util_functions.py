"""
	Tests for util_functions.py
"""
from util_functions import ZipDataHandler


TEST_ZIP = 'tests/test_data.zip'
ZDH = ZipDataHandler(TEST_ZIP)



def test_get_file_names():
	"""
		Test if all file names are present
	"""
	fn = ZDH.zip_file_names
	assert len(fn) == 4
	assert fn[0] == 'abcdefg'


def test_shuffle_file_names():
	"""
		Randomly shuffling file names
	"""
	original_zero = ZDH.zip_file_names[0]
	original_one = ZDH.zip_file_names[1]
	ZDH.shuffle_file_names()
	new_zero = ZDH.zip_file_names[0]
	new_one = ZDH.zip_file_names[1]

	assert original_zero != new_zero or original_one != new_one

def test_sort_filenames_by_size():
	"""
		Test sort files by filesize
	"""
	ZDH.sort_files_by_size()
	fn = ZDH.zip_file_names

	assert fn[0] == 'wxyz'
	assert fn[3] == 'hijklmnop'


def test_load_file():
	"""
		Tests if it loads binary and converts to hex
		correctly
	"""
	hex_string = ZDH._load_file('wxyz')
	assert hex_string == b'7778797a'


def test_split_string():
	"""
		Tests if splits hex string into 
		regular strings of byte words
	"""
	hex_string = b'7778797a'
	byte_word_array = ZDH._split_string(hex_string)
	assert byte_word_array == ['7778', '797a']


def test_generate_batch():
	"""
		Tests if it generates a batch correctly
	"""
	current_index = 1
	batch_size = 2
	batch = ZDH.generate_batch(current_index, batch_size)
	assert len(batch) == batch_size
