import os
import sys

# Hack to work around Python 3.8+ secure dll loading:
# see https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew
if hasattr(os, "add_dll_directory"):
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isdir(directory):
            os.add_dll_directory(directory)

PY2 = (2, 0) <= sys.version_info < (3, 0)
PY3 = (3, 0) <= sys.version_info < (4, 0)

use_2to3 = True
if PY2:
    subdir = "py2"
    from distutils.core import setup, Extension
elif PY3:
    subdir = "py3"
    from setuptools import setup, Extension, __version__ as setuptools_versions
    from conans import tools
    use_2to3 = tools.Version(setuptools_versions) <= tools.Version("58.0.0")
else:
    raise Exception


setup(
    name="test_package",
    version="1.0",
    use_2to3=use_2to3,
    ext_modules=[
        Extension("spam", [os.path.join(subdir, "test_module.c")]),
    ],
)
