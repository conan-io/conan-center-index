from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.9"


class TimsortConan(ConanFile):
    name = "timsort"
    description = "A C++ implementation of timsort"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/timsort/cpp-TimSort"
    topics = ("sorting", "algorithms", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        if Version(self.version) < "2.0.0":
            return "98"
        if Version(self.version) < "3.0.0":
            return "11"
        return "20"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gfx-timsort")
        self.cpp_info.set_property("cmake_target_name", "gfx::timsort")
        self.cpp_info.components["gfx-timsort"].set_property("cmake_target_name", "gfx::timsort")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
