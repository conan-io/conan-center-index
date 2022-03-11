import functools
import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class QDBMConan(ConanFile):
    name = "qdbm"
    description = "QDBM is a library of routines for managing a database."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://fallabs.com/qdbm/"
    topics = ("qdbm", "database", "db")
    license = "LGPL-2.1-or-later"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_pthread": [True, False],
        "with_iconv": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_pthread": True,
        "with_iconv": True,
        "with_zlib": True,
    }
    generators = ("cmake", "cmake_find_package_multi")
    exports_sources = ("CMakeLists.txt",)
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_pthread

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_iconv:
            self.requires("libiconv/1.16")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_qdbm_VERSION"] = self.version
        cmake.definitions["MYICONV"] = self.options.with_iconv
        cmake.definitions["MYZLIB"] = self.options.with_zlib
        cmake.definitions["MYPTHREAD"] = self.options\
            .get_safe("with_pthread", False)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", "licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["qdbm"]
        if self.options.get_safe("with_pthread"):
            self.cpp_info.system_libs.append("pthread")
