from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMakeToolchain

import os

required_conan_version = ">=1.47.0"


class CircularBufferConan(ConanFile):
    name = "circularbuffer"
    description = "Arduino circular buffer library"
    topics = ("circular buffer", "arduino", "data-structures")
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rlogiacco/CircularBuffer"
    no_copy_source = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder,
             "licenses"), src=self.source_folder)
        copy(self, "CircularBuffer.h",
             dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "CircularBuffer.tpp",
             dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_id(self):
        self.info.clear()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CircularBuffer")
        self.cpp_info.set_property(
            "cmake_target_name", "CircularBuffer::CircularBuffer")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "CircularBuffer"
        self.cpp_info.filenames["cmake_find_package_multi"] = "CircularBuffer"
        self.cpp_info.names["cmake_find_package"] = "CircularBuffer"
        self.cpp_info.names["cmake_find_package_multi"] = "CircularBuffer"
