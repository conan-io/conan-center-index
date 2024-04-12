from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=1.50.0"


class CircularBufferConan(ConanFile):
    name = "circularbuffer"
    description = "Arduino circular buffer library"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rlogiacco/CircularBuffer"
    topics = ("circular buffer", "arduino", "data-structures", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "CircularBuffer.h*",
             dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "CircularBuffer.tpp",
             dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
