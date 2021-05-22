from conans import ConanFile, CMake, tools
import os
from conans.tools import load
from conans.errors import ConanInvalidConfiguration
from pathlib import Path
import textwrap

class FastDDSConan(ConanFile):

    name = "fast-dds"
    license = "Apache-2.0"
    version = "2.3.2"
    homepage = "https://fast-dds.docs.eprosima.com/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The most complete DDS - Proven: Plenty of success cases."
    topics = ("Memory","Allocator")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":          [True, False]
    }
    default_options = {
        "shared":            False
    }
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _pkg_cmake(self):
        return os.path.join(
            self.package_folder,
            "lib",
            "foonathan_memory",
            "cmake"
        )
    
    @property
    def _pkg_lib(self):
        return os.path.join(
            self.package_folder,
            "lib"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _get_configured_cmake(self):
        if self._cmake:
            pass 
        else:
            self._cmake = CMake(self)
        self._cmake.definitions["BUILD_MEMORY_TOOLS"] = False
        self._cmake.configure(
            source_dir = self._source_subfolder
        )
        return self._cmake

    def requirements(self):
        self.requires("tinyxml2/7.1.0")
        self.requires("asio/1.11.0@bincrafters/stable")
        self.requires("fast-cdr/1.0.21")
        self.requires("foo-mem-ven/1.1.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build(self):

        cmake = self._get_configured_cmake()
        cmake.build()

    def package(self):
        cmake = self._get_configured_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        lib = tools.relative_dirs(self._pkg_lib)[0]
        lib_new = lib.replace("-0.6.2-dbg","") \
                     .replace("-0.6.2","")
        tools.rename(
            os.path.join(self._pkg_lib,lib),
            os.path.join(self._pkg_lib,lib_new)
        )
        tools.rmdir(self._pkg_cmake)
        tools.rmdir(self._pkg_share)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "foonathan_memory"
        self.cpp_info.names["cmake_find_multi_package"] = "foonathan_memory"
        self.cpp_info.libs = ["foonathan_memory"]
