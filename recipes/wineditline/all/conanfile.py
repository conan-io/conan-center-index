import functools
import os

from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

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
    exports_sources = ("patches/*", "CMakeLists.txt")

    def validate(self):
        if self.settings.os != "Windows":
            message = "wineditline is supported only on Windows."
            raise ConanInvalidConfiguration(message)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        self._configure_cmake().build()

    def package(self):
        self.copy("COPYING", "licenses", self._source_subfolder)
        self._configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["edit"]
