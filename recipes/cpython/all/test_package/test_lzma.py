import lzma


data = lzma.compress(b"hello world")
if data is None:
    raise Exception
