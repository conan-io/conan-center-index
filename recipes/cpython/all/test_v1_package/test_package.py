import argparse
import os
import sys

# Hack to work around Python 3.8+ secure dll loading
# See https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew
if hasattr(os, "add_dll_directory"):
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isdir(directory):
            os.add_dll_directory(directory)

ALL_TESTS = dict()


def add_test(fn):
    global ALL_TESTS
    name = fn.__name__[fn.__name__.find("_")+1:]

    def inner_fn():
        print("testing {}".format(name))
        sys.stdout.flush()
        fn()
    ALL_TESTS[name] = inner_fn
    return fn


@add_test
def test_expat():
    import xml.parsers.expat

    # 3 handler functions
    def start_element(name, attrs):
        print('Start element:', name, attrs)

    def end_element(name):
        print('End element:', name)

    def char_data(data):
        print('Character data:', repr(data))

    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data

    p.Parse("""<?xml version="1.0"?>
    <parent id="top"><child1 name="paul">Text goes here</child1>
    <child2 name="fred">More text</child2>
    </parent>""", 1)


@add_test
def test_gdbm():
    if sys.version_info < (3, 0):
        import gdbm
    else:
        import dbm.gnu as gdbm

    dbfile = "gdbm.db"

    db = gdbm.open(dbfile, "c")
    db["key1"] = "data1"
    db["key2"] = "data2"
    db.close()

    db = gdbm.open(dbfile, "r")
    print("keys read from", dbfile, "are", db.keys())
    if len(db.keys()) != 2:
        raise Exception("Wrong length")
    if b"key1" not in db.keys():
        raise Exception("key1 not present")
    if b"key2" not in db.keys():
        raise Exception("key2 not present")


@add_test
def test_spam():
    import platform

    print("About to import spam")
    sys.stdout.flush()
    import spam

    if "This is an example spam doc." not in spam.__doc__:
        raise Exception("spam.__doc__ does not contain the expected text")

    cmd = {
        "Windows": "dir",
    }.get(platform.system(), "ls")
    print("About to run spam.system(\"{}\")".format(cmd))
    sys.stdout.flush()

    spam.system(cmd)


@add_test
def test_bz2():
    import bz2

    compressed = bz2.compress(b"hellow world")
    if compressed is None:
        raise Exception("bz2.compress returned no data")


@add_test
def test_bsddb():
    import bsddb

    db = bsddb.btopen("bsddb.db", "c")
    db["key1"] = "value1"
    db["key2"] = "value2"
    db.close()

    db = bsddb.btopen("bsddb.db", "r")
    if len(db) != 2:
        raise Exception("Wrong length")
    if db["key1"] != "value1":
        raise Exception("value1 incorrect {}".format(db["key1"]))
    if db["key2"] != "value2":
        raise Exception("value2 incorrect {}".format(db["key2"]))


@add_test
def test_lzma():
    import lzma

    data = lzma.compress(b"hello world")
    if data is None:
        raise Exception("lzma.compress returned no data")


@add_test
def test_sqlite3():
    import sqlite3
    conn = sqlite3.connect("sqlite3.db")

    c = conn.cursor()
    c.execute("""CREATE TABLE stocks
                 (date text, trans text, symbol text, qty real, price real)""")
    c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
    conn.commit()

    t = ('RHAT',)
    c.execute('SELECT * FROM stocks WHERE symbol=?', t)

    # Larger example that inserts many records at a time
    purchases = [
        ('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
        ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
        ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
    ]
    c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)
    conn.commit()
    conn.close()
    conn = sqlite3.connect("sqlite3.db")
    c = conn.cursor()
    c.execute("SELECT * from stocks")
    data = c.fetchall()
    if len(data) != 4:
        raise Exception("Need 4 stocks")
    print(data)
    conn.close()


@add_test
def test_decimal():
    if sys.version_info >= (3, ):
        # Check whether the _decimal package was built successfully
        import _decimal as decimal
    else:
        import decimal
    decimal.getcontext().prec = 6
    print("1/7 =", decimal.Decimal(1) / decimal.Decimal(7))
    decimal.getcontext().prec = 40
    print("1/7 =", decimal.Decimal(1) / decimal.Decimal(7))


@add_test
def test_curses():
    import _curses

    print("Using _curses version {}".format(_curses.version))


@add_test
def test_ctypes():
    import _ctypes

    errno = _ctypes.get_errno()
    print("errno={}".format(errno))


@add_test
def test_tkinter():
    import _tkinter

    print("tcl version: {}".format(_tkinter.TCL_VERSION))
    print("tk version: {}".format(_tkinter.TK_VERSION))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="build_folder", help="build_folder", required=True)
    parser.add_argument("-t", dest="test_module", help="test python module")
    ns = parser.parse_args()

    os.chdir(ns.build_folder)
    ALL_TESTS[ns.test_module]()


if __name__ == "__main__":
    main()
