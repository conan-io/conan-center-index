from conan import ConanFile
from conan.tools.files import copy, get, save
from conan.tools.scm import Version
import os
import shutil
import textwrap


class SConsConan(ConanFile):
    name = "scons"
    description = "SCons is an Open Source software construction tool-that is, a next-generation build tool"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://scons.org"
    topics = ("scons", "build", "configuration", "development")
    settings = "os"
    package_type = "application"
    no_copy_source = True
    short_paths = True

    def layout(self):
        self.folders.source = "src"

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def _chmod_x(self, path):
        if os.name == "posix":
            os.chmod(path, 0o755)

    @property
    def _scons_sh(self):
        return os.path.join(self.package_folder, "bin", "scons")

    @property
    def _scons_cmd(self):
        return os.path.join(self.package_folder, "bin", "scons.cmd")

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        if Version(self.version) < 4:
            shutil.copytree(os.path.join(self.source_folder, "engine", "SCons"),
                            os.path.join(self.package_folder, "res", "SCons"))
        else:
            shutil.copytree(os.path.join(self.source_folder, "SCons"),
                            os.path.join(self.package_folder, "res", "SCons"))

        save(self, self._scons_sh, textwrap.dedent("""\
            #!/bin/sh

            realpath() (
              local startpwd=$PWD
              cd "$(dirname "$1")"
              local ourlink=$(readlink "$(basename "$1")")
              while [ "$ourlink" ]; do
                cd "$(dirname "$ourlink")"
                local ourlink=$(readlink "$(basename "$1")")
              done
              local ourrealpath="$PWD/$(basename "$1")"
              cd "$startpwd"
              echo "$ourrealpath"
            )

            currentdir="$(dirname "$(realpath "$0")")"

            export PYTHONPATH="$currentdir/../res:$PYTHONPATH"
            exec ${PYTHON:-python3} "$currentdir/../res/SCons/__main__.py" "$@"
        """))
        self._chmod_x(self._scons_sh)
        save(self, self._scons_cmd, textwrap.dedent(r"""
            @echo off
            set currentdir=%~dp0
            if not defined PYTHON (
                set PYTHON=python
            )
            set PYTHONPATH=%currentdir%\\..\\res;%PYTHONPATH%
            CALL %PYTHON% %currentdir%\\..\\res\\SCons\\__main__.py %*
        """))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        self._chmod_x(self._scons_sh)
        bindir = os.path.join(self.package_folder, "bin")

        # For Conan 1.x downstream consumers, can be removed once recipe is Conan 2.x only:
        self.output.info("Appending PATH environment var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        if self.settings.os == "Windows":
            scons_bin = os.path.join(bindir, "scons.cmd")
        else:
            scons_bin = os.path.join(bindir, "scons")
        self.user_info.scons = scons_bin
        self.output.info("Setting SCONS environment variable: {}".format(scons_bin))
        self.env_info.SCONS = scons_bin
