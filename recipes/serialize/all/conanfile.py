import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.19.0"


class SerializeConan(ConanFile):
    name = "serialize"
    description = "A simple bitpacking serializer for C++"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mas-bandwidth/serialize"
    topics = ("serialization", "bitpacking", "games", "networking", "header-only")
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
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        # The single header lives at the repo root. Upstream's CMake install rule
        # would place it in include/ exactly the same way, so running CMake for
        # one file is skipped entirely.
        copy(self, "serialize.h", self.source_folder,
             os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Match upstream's exported serialize-config.cmake / serialize::serialize
        # so find_package(serialize) consumers are source-compatible.
        self.cpp_info.set_property("cmake_file_name", "serialize")
        self.cpp_info.set_property("cmake_target_name", "serialize::serialize")

