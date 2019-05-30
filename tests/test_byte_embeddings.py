"""
    Tests for byte_embeddings.py
"""
from byte_embeddings import train_model
from util_functions import ZipDataHandler


TEST_ZIP = 'tests/test_data.zip'
ZDH = ZipDataHandler(TEST_ZIP)


def test_train_new_model():
    """
        Test whether it can train a new model
    """
    current_index = 1
    batch_size = 2
    batch, _ = ZDH.generate_batch(current_index, batch_size)
    w2v_model = None
    w2v_model = train_model(batch, w2v_model)
    assert w2v_model is not None


def test_update_model():
    """
        Test whether it can update an existing model
    """
    batch_size = 2
    w2v_model = None
    num_files = ZDH.num_files
    for idx in range(0, num_files, batch_size):
        batch, _ = ZDH.generate_batch(idx, batch_size)
        w2v_model = train_model(batch, w2v_model)
    assert w2v_model.wv['7778'] is not None
    assert w2v_model.wv['6869'] is not None
