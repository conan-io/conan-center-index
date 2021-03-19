from conans import ConanFile, tools
import os


class MesonInstallerConan(ConanFile):
    name = "meson"
    description = "Meson is a project to create the best possible next-generation build system"
    topics = ("conan", "meson", "mesonbuild", "build-system")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mesonbuild/meson"
    license = "Apache-2.0"
    no_copy_source = True

    _source_subfolder = "source_subfolder"
    _meson_cmd = """@echo off
CALL python %~dp0/meson.py %*
"""
    _meson_sh = """#!/usr/bin/env bash
meson_dir=$(dirname "$0")
exec "$meson_dir/meson.py" "$@"
"""

    def requirements(self):
        self.requires("ninja/1.10.2")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "meson-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        # create wrapper scripts
        with open(os.path.join(self._source_subfolder, "meson.cmd"), "w") as f:
            f.write(self._meson_cmd)
        with open(os.path.join(self._source_subfolder, "meson"), "w") as f:
            f.write(self._meson_sh)

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="bin", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "bin", "test cases"))

    def package_info(self):
        meson_root = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % meson_root)
        self.env_info.PATH.append(meson_root)

        self._chmod_plus_x(os.path.join(meson_root, "meson"))
        self._chmod_plus_x(os.path.join(meson_root, "meson.py"))

        self.cpp_info.builddirs = [os.path.join("bin", "mesonbuild", "cmake", "data")]
