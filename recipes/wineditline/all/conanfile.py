import functools
import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class WineditlineConan(ConanFile):
    name = "wineditline"
    description = (
        "A BSD-licensed EditLine API implementation for the native "
        "Windows Console"
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mingweditline.sourceforge.net/"
    topics = ("readline", "editline", "windows")
    license = "BSD-3-Clause"
    generators = ("cmake",)
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    exports_sources = ("CMakeLists.txt",)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Windows":
            message = "wineditline is supported only on Windows."
            raise ConanInvalidConfiguration(message)

    def source(self):
        root = self._source_subfolder
        get_args = self.conan_data["sources"][self.version]
        tools.get(**get_args, destination=root, strip_root=True)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", "licenses", self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        name = self.name
        info = self.cpp_info

        info.set_property("cmake_file_name", name)
        info.set_property("cmake_target_name", f"{name}::{name}")

        info.names.update({
            "cmake_find_package": name,
            "cmake_find_package_multi": name,
        })

        info.libs = ["edit"]
