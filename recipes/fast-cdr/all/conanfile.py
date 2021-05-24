from conans import ConanFile, CMake, tools
import os
from conans.tools import load
from conans.errors import ConanInvalidConfiguration
from pathlib import Path
import textwrap

class FastCDRConan(ConanFile):

    name = "fast-cdr"
    license = "Apache-2.0"
    homepage = "https://github.com/eProsima/Fast-CDR"
    url = "https://github.com/conan-io/conan-center-index"
    description = "eProsima FastCDR library for serialization"
    topics = ("conan","DDS", "Middleware","Serialization")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":          [True, False],
        "fPIC":            [True, False]
    }
    default_options = {
        "shared":            False,
        "fPIC":              True
    }
    exports_sources = ["patches/**"]
    _cmake = None

    @property
    def _pkg_cmake(self):
        return os.path.join(
            self.package_folder,
            "lib",
            "cmake"
        )

    @property
    def _pkg_share(self):
        return os.path.join(
            self.package_folder,
            "share"
        )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _get_configured_cmake(self):
        if self._cmake:
            pass 
        else:
            self._cmake = CMake(self)
        self._cmake.configure(
            source_dir = self._source_subfolder
        )
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Linux":
            if (self.settings.compiler == "gcc" and self.settings.compiler.libcxx == "libstdc++"):
                raise ConanInvalidConfiguration("This package requires libstdc++11 for libcxx setting")
            if (self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libstdc++"):
                raise ConanInvalidConfiguration("This package requires libstdc++11 for libcxx setting")

    def build(self):
        self._patch_sources()

        cmake = self._get_configured_cmake()
        cmake.build()

    def package(self):
        cmake = self._get_configured_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(self._pkg_cmake)
        tools.rmdir(self._pkg_share)
        
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "fastcdr"
        self.cpp_info.names["cmake_find_package_multi"] = "fastcdr"
        self.cpp_info.libs = ["fastcdr"]
