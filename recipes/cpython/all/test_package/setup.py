import os
import sys


PY2 = (2, 0) <= sys.version_info < (3, 0)
PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY2:
    subdir = "py2"
    from distutils.core import setup, Command, Extension
    from distutils.command.build import build as BuildCmd
elif PY3:
    subdir = "py3"
    from setuptools import setup, Command, Extension
    from setuptools.command.build_ext import build_ext as BuildCmd
else:
    raise Exception

spam_sources = [os.path.join(os.path.dirname(os.path.realpath(__file__)), subdir, "test_module.c")]


class ConanBuild2Command(BuildCmd):
    description = "build everything with includes and libs from conan"

    user_options = [
        ("install-folder=", None, "Install folder of conan"),
        ("nolink", None, "Don't link to installed conan dependency libraries"),
    ] + BuildCmd.user_options

    boolean_options = ["nolink"] + BuildCmd.boolean_options

    def initialize_options(self):
        BuildCmd.initialize_options(self)
        self.install_folder = None
        self.nolink = False

    def finalize_options(self):
        if self.install_folder is None:
            self.install_folder = os.getcwd()
        BuildCmd.finalize_options(self)

    def read_conanbuildinfo(self):
        data = {}
        current_section = None
        with open(os.path.join(self.install_folder, "conanbuildinfo.txt")) as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                    data[current_section] = []
                    continue
                data[current_section].append(line)
        return data

    def run(self):
        conanbuildinfo = self.read_conanbuildinfo()
        for extmod in self.distribution.ext_modules:
            extmod.include_dirs.extend(conanbuildinfo["includedirs"])
            extmod.library_dirs.extend(conanbuildinfo["libdirs"])
            if not self.nolink:
                extmod.libraries.extend(conanbuildinfo["libs"])
        BuildCmd.run(self)


setup(
    name="test_package",
    version="1.0",
    use_2to3=True,
    ext_modules=[
        Extension("spam", spam_sources),
    ],
    cmdclass={
        "conan_build": ConanBuild2Command,
    },
)
