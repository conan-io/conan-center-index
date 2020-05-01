import bz2


compressed = bz2.compress(b"hellow world")
if compressed is None:
    raise Exception
