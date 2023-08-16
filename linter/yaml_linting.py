import argparse


def file_path(a_string):
    from os.path import isfile

    if not isfile(a_string):
        raise argparse.ArgumentTypeError(f"{a_string} does not point to a file")
    return a_string
