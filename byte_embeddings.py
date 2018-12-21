"""
    Demo code for training embeddings on byte code
"""
import argparse
from zipfile import ZipFile


def get_file_names(zip_file_name):
    with ZipFile(zip_file_name, 'r') as zip:
        file_names = zip.namelist()
    return file_names


def open_file(zip_file_name, file_name):
    with ZipFile(zip_file_name, 'r') as zip:
        file = zip.open(file_name)
    return file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract zip files')

    parser.add_argument('--zip_file_name', help='foo help')
    args = parser.parse_args()

    fn = get_file_names(args.zip_file_name)

    for f in fn[0:1]:
        print('opening: ', f)
        print(open_file(args.zip_file_name, f))
