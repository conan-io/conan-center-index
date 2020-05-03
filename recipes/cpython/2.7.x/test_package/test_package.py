import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-b", dest="build_folder", help="build_folder", required=True)
parser.add_argument("-t", dest="test_module", help="test python module")
ns = parser.parse_args()

os.chdir(ns.build_folder)


all_tests = dict()


def add_test(fn):
    global all_tests
    name = fn.__name__[fn.__name__.find("_")+1:]
    def inner_fn():
        print("testing {}".format(name))
        sys.stdout.flush()
        fn()
    all_tests[name] = inner_fn
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
    import gdbm

    dbfile = "data.db"

    db = gdbm.open(dbfile, "c")
    db["key1"] = "data1"
    db["key2"] = "data2"
    db.close()

    db = gdbm.open(dbfile, "r")
    print("keys read from", dbfile, "are", db.keys())
    if len(db.keys()) != 2:
        raise Exception("Wrong length")
    if "key1" not in db.keys():
        raise Exception("key1 not present")
    if "key2" not in db.keys():
        raise Exception("key2 not present")


@add_test
def test_spam():
    import spam

    if "This is an example spam doc." not in spam.__doc__:
        raise Exception("spam.__doc__ does not contain the expected text")

    spam.system("dir")


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


all_tests[ns.test_module]()
