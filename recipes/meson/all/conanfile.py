from conans import ConanFile, tools
import os
import textwrap

required_conan_version = ">=1.33.0"


class MesonInstallerConan(ConanFile):
    name = "meson"
    description = "Meson is a project to create the best possible next-generation build system"
    topics = ("meson", "mesonbuild", "build-system")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mesonbuild/meson"
    license = "Apache-2.0"
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("ninja/1.10.2")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

        # create wrapper scripts
        tools.save(os.path.join(self._source_subfolder, "meson.cmd"), textwrap.dedent("""\
            @echo off
            CALL python %~dp0/meson.py %*
        """))
        tools.save(os.path.join(self._source_subfolder, "meson"), textwrap.dedent("""\
            #!/usr/bin/env bash
            meson_dir=$(dirname "$0")
            exec "$meson_dir/meson.py" "$@"
        """))

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package(self):
        # FIXME: https://github.com/conan-io/conan/issues/10726
        def _fix_symlinks(root, files):
            if not tools.os_info.is_windows:
                return
            for filename in files:
                filename = os.path.join(root, filename)
                if os.path.islink(filename):
                    target = os.readlink(filename)
                    if "/" in target:
                        self.output.info("fixing broken link {}".format(target))
                        target = target.replace("/", "\\")
                        os.unlink(filename)
                        os.symlink(target, filename)

        for root, dirs, files in os.walk(self.source_folder, self._source_subfolder):
            _fix_symlinks(root, dirs)
            _fix_symlinks(root, files)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="bin", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "bin", "test cases"))

    def package_info(self):
        meson_root = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(meson_root))
        self.env_info.PATH.append(meson_root)

        self._chmod_plus_x(os.path.join(meson_root, "meson"))
        self._chmod_plus_x(os.path.join(meson_root, "meson.py"))

        self.cpp_info.builddirs = [os.path.join("bin", "mesonbuild", "cmake", "data")]

        self.cpp_info.includedirs = []
