from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get
import os


required_conan_version = ">=2.0.9"


class TinyOptionalConan(ConanFile):
    name = "tiny-optional"
    description = "Replacement for std::optional that does not waste memory unnecessarily"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Sedeniono/tiny-optional"
    topics = ("optional", "memory-efficiency", "cache-friendly", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "tiny-optional")
        self.cpp_info.set_property("cmake_target_name", "tiny-optional::tiny-optional")
