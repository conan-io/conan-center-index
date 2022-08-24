from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import contextlib
import os
import textwrap

required_conan_version = ">=1.33.0"


class LzipConan(ConanFile):
    name = "lzip"
    description = "Lzip is a lossless data compressor with a user interface similar to the one of gzip or bzip2"
    topics = ("lzip", "compressor", "lzma")
    license = "GPL-v2-or-later"
    homepage = "https://www.nongnu.org/lzip/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/**"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported")

    def package_id(self):
        del self.info.settings.compiler

    def _detect_compilers(self):
        tools.files.rmdir(self, "detectdir")
        tools.files.mkdir(self, "detectdir")
        with tools.files.chdir(self, "detectdir"):
            tools.files.save(self, "CMakeLists.txt", textwrap.dedent("""\
                cmake_minimum_required(VERSION 2.8)
                project(test C CXX)
                message(STATUS "CC=${CMAKE_C_COMPILER}")
                message(STATUS "CXX=${CMAKE_CXX_COMPILER}")
                file(WRITE cc.txt "${CMAKE_C_COMPILER}")
                file(WRITE cxx.txt "${CMAKE_CXX_COMPILER}")
                """))
            CMake(self).configure(source_folder="detectdir", build_folder="detectdir")
            cc = tools.files.load(self, "cc.txt").strip()
            cxx = tools.files.load(self, "cxx.txt").strip()
        return cc, cxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
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
            tools.files.patch(self, **patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            with tools.environment_append({"CONAN_CPU_COUNT": "1"}):
                autotools.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
