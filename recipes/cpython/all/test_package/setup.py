import os
import sys

# Hack to work around Python 3.8+ secure dll loading:
# see https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew
if hasattr(os, "add_dll_directory"):
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isdir(directory):
            os.add_dll_directory(directory)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    subdir = "py2"
    from distutils.core import setup, Extension
elif PY3:
    subdir = "py3"
    from setuptools import setup, Extension
else:
    raise Exception

script_dir = os.path.dirname(os.path.realpath(__file__))

setup(
    name="test_package",
    version="1.0",
    use_2to3=True,
    ext_modules=[
        Extension("spam", [os.path.join(script_dir, subdir, "test_module.c")]),
    ],
)
