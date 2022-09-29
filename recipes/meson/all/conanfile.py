from conan import ConanFile
from conan.tools.files import copy, get, rmdir, save
from conan.tools.layout import basic_layout
import os
import textwrap

required_conan_version = ">=1.50.0"


class MesonConan(ConanFile):
    name = "meson"
    description = "Meson is a project to create the best possible next-generation build system"
    topics = ("meson", "mesonbuild", "build-system")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mesonbuild/meson"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("ninja/1.11.0")

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

        # FIXME: https://github.com/conan-io/conan/issues/10726
        def _fix_symlinks(root, files):
            if not self._settings_build.os == "Windows":
                return
            for filename in files:
                filename = os.path.join(root, filename)
                if os.path.islink(filename):
                    target = os.readlink(filename)
                    if "/" in target:
                        self.output.info(f"fixing broken link {target}")
                        target = target.replace("/", "\\")
                        os.unlink(filename)
                        os.symlink(target, filename)

        for root, dirs, files in os.walk(self.source_folder):
            _fix_symlinks(root, dirs)
            _fix_symlinks(root, files)

    def build(self):
        pass

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "bin", "test cases"))

        # create wrapper scripts
        save(self, os.path.join(self.package_folder, "bin", "meson.cmd"), textwrap.dedent("""\
            @echo off
            CALL python %~dp0/meson.py %*
        """))
        save(self, os.path.join(self.package_folder, "bin", "meson"), textwrap.dedent("""\
            #!/usr/bin/env bash
            meson_dir=$(dirname "$0")
            exec "$meson_dir/meson.py" "$@"
        """))

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        meson_root = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {meson_root}")
        self.env_info.PATH.append(meson_root)

        self._chmod_plus_x(os.path.join(meson_root, "meson"))
        self._chmod_plus_x(os.path.join(meson_root, "meson.py"))

        self.cpp_info.builddirs = [os.path.join("bin", "mesonbuild", "cmake", "data")]

        self.cpp_info.frameworkdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
