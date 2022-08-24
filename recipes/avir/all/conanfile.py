import os

from conan.errors import ConanInvalidConfiguration
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"

class AVIRConan(ConanFile):
    name = "avir"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "High-quality pro image resizing / scaling C++ library, image resize"
    topics = ("image-processing", "image-resizer", "lanczos", )
    homepage = "https://github.com/avaneev/avir"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "avir"
        self.cpp_info.filenames["cmake_find_package_multi"] = "avir"
