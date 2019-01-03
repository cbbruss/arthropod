"""
	Tests for embed_binary.py
"""
from byte_embeddings import train_model
from util_functions import ZipDataHandler
from embed_binary import embed_batch


TEST_ZIP = 'tests/test_data.zip'
ZDH = ZipDataHandler(TEST_ZIP)


def test_embed_batch():
	"""
		Test if batch correctly is embedded
	"""
	batch_size = 2
	w2v_model = None
	num_files = ZDH.num_files
	for idx in range(0, num_files, batch_size):
	    batch = ZDH.generate_batch(idx, batch_size)
	    w2v_model = train_model(batch, w2v_model)
	embedding_dim = 256
	count_half_words = 0
	max_size = max([len(x) for x in batch])
	embedded_batch, count_half_words = embed_batch(w2v_model, 
												   batch, 
												   max_size,
												   embedding_dim,
												   count_half_words)

	assert embedded_batch.shape == (batch_size, max_size, embedding_dim)