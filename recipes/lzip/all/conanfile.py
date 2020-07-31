from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import textwrap


class LzipConan(ConanFile):
    name = "lzip"
    description = "Lzip is a lossless data compressor with a user interface similar to the one of gzip or bzip2"
    topics = ("conan", "lzip", "compressor", "lzma")
    license = "GPL-v2-or-later"
    homepage = "https://www.nongnu.org/lzip/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _detect_compilers(self):
        tools.rmdir("detectdir")
        tools.mkdir("detectdir")
        with tools.chdir("detectdir"):
            tools.save("CMakeLists.txt", textwrap.dedent("""\
                cmake_minimum_required(VERSION 2.8)
                project(test C CXX)
                message(STATUS "CC=${CMAKE_C_COMPILER}")
                message(STATUS "CXX=${CMAKE_CXX_COMPILER}")
                file(WRITE cc.txt "${CMAKE_C_COMPILER}")
                file(WRITE cxx.txt "${CMAKE_CXX_COMPILER}")
                """))
            CMake(self).configure(source_folder="detectdir", build_folder="detectdir")
            cc = tools.load("cc.txt").strip()
            cxx = tools.load("cxx.txt").strip()
        return cc, cxx

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env = {}
        cc, cxx = self._detect_compilers()
        if not tools.get_env("CC"):
            env["CC"] = cc
        if not tools.get_env("CXX"):
            env["CXX"] = cxx
        with tools.environment_append(env):
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            with tools.environment_append({"CONAN_CPU_COUNT": "1"}):
                autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
