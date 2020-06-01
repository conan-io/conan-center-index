import os
import sys


PY2 = (2, 0) <= sys.version_info < (3, 0)
PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY2:
    subdir = "py2"
    from distutils.core import setup, Extension
elif PY3:
    subdir = "py3"
    from setuptools import setup, Extension
else:
    raise Exception

spam_sources = [os.path.join(os.path.dirname(os.path.realpath(__file__)), subdir, "test_module.c")]


setup(
    name="test_package",
    version="1.0",
    use_2to3=True,
    ext_modules=[
        Extension("spam", spam_sources),
    ],
)
