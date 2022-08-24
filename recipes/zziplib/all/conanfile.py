from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.36.0"


class ZziplibConan(ConanFile):
    name = "zziplib"
    description = "The ZZIPlib provides read access on ZIP-archives and unpacked data"
    topics = ("zip", "archive", "decompression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gdraheim/zziplib"
    license = "GPL-2.0-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "zzipmapped": [True, False],
        "zzipfseeko": [True, False],
        "zzipwrap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zzipmapped": True,
        "zzipfseeko": True,
        "zzipwrap": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["ZZIPCOMPAT"] = self.settings.os != "Windows"
        cmake.definitions["ZZIPMMAPPED"] = self.options.zzipmapped
        cmake.definitions["ZZIPFSEEKO"] = self.options.zzipfseeko
        cmake.definitions["ZZIPWRAP"] = self.options.zzipwrap
        cmake.definitions["ZZIPSDL"] = False
        cmake.definitions["ZZIPBINS"] = False
        cmake.definitions["ZZIPTEST"] = False
        cmake.definitions["ZZIPDOCS"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="COPYING.LIB", dst="licenses", src=self._source_subfolder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "zziplib-all-do-not-use")

        # libzzip
        self.cpp_info.components["zzip"].set_property("pkg_config_name", "zziplib")
        self.cpp_info.components["zzip"].libs = [self._get_decorated_lib("zzip")]
        self.cpp_info.components["zzip"].requires = ["zlib::zlib"]
        # libzzipmmapped
        if self.options.zzipmapped:
            self.cpp_info.components["zzipmmapped"].set_property("pkg_config_name", "zzipmmapped")
            self.cpp_info.components["zzipmmapped"].libs = [self._get_decorated_lib("zzipmmapped")]
            self.cpp_info.components["zzipmmapped"].requires = ["zlib::zlib"]
        # libzzipfseeko
        if self.options.zzipfseeko:
            self.cpp_info.components["zzipfseeko"].set_property("pkg_config_name", "zzipfseeko")
            self.cpp_info.components["zzipfseeko"].libs = [self._get_decorated_lib("zzipfseeko")]
            self.cpp_info.components["zzipfseeko"].requires = ["zlib::zlib"]
        # libzzipwrap
        if self.options.zzipwrap:
            self.cpp_info.components["zzipwrap"].set_property("pkg_config_name", "zzipwrap")
            self.cpp_info.components["zzipwrap"].libs = [self._get_decorated_lib("zzipwrap")]
            self.cpp_info.components["zzipwrap"].requires = ["zzip", "zlib::zlib"]

    def _get_decorated_lib(self, name):
        suffix = ""
        if self.settings.build_type == "Release":
            suffix += "-" + tools.Version(self.version).major
        return name + suffix
