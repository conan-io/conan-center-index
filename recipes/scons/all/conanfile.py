from conans import ConanFile, tools
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
    settings = "os"  # Added to let the CI test this package on all os'es

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _chmod_x(self, path):
        if os.name == "posix":
            os.chmod(path, 0o755)

    @property
    def _scons_sh(self):
        return os.path.join(self.package_folder, "bin", "scons")

    @property
    def _scons_bat(self):
        return os.path.join(self.package_folder, "bin", "scons.bat")

    def package(self):
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses")

        if tools.Version(self.version) < 4:
            shutil.copytree(os.path.join(self._source_subfolder, "engine", "SCons"),
                            os.path.join(self.package_folder, "res", "SCons"))
        else:
            shutil.copytree(os.path.join(self._source_subfolder, "SCons"),
                            os.path.join(self.package_folder, "res", "SCons"))

        tools.save(self._scons_sh, textwrap.dedent("""\
            #!/bin/bash

            currentdir="$(dirname "$(readlink -f "$0")")"

            export PYTHONPATH="$currentdir/../res:$PYTHONPATH"
            exec ${PYTHON:-python} "$currentdir/../res/SCons/__main__.py" $*
        """))
        self._chmod_x(self._scons_sh)

        tools.save(self._scons_bat, textwrap.dedent(r"""
            @echo off
            set currentdir=%~dp0
            if not defined PYTHON (
                set PYTHON=python
            )
            %PYTHON% "%currentdir%\\..\\res\\SCons\\__main__.py" %*
            exit /B %ERRORLEVEL%
        """))

        # Mislead CI and create an empty header in the include directory
        include_dir = os.path.join(self.package_folder, "include")
        os.mkdir(include_dir)
        tools.save(os.path.join(include_dir, "__nop.h"), "")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        self._chmod_x(self._scons_sh)

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(bindir))
        self.env_info.PATH.append(bindir)
