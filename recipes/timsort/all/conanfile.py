from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class TimsortConan(ConanFile):
    name = "timsort"
    description = "A C++ implementation of timsort"
    topics = ("sorting", "algorithms")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/timsort/cpp-TimSort"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if Version(self.version) >= "2.0.0":
                check_min_cppstd(self, 11)

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
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "gfx-timsort"
        self.cpp_info.filenames["cmake_find_package_multi"] = "gfx-timsort"
        self.cpp_info.names["cmake_find_package"] = "gfx"
        self.cpp_info.names["cmake_find_package_multi"] = "gfx"
        self.cpp_info.components["gfx-timsort"].names["cmake_find_package"] = "timsort"
        self.cpp_info.components["gfx-timsort"].names["cmake_find_package_multi"] = "timsort"
        self.cpp_info.components["gfx-timsort"].set_property("cmake_target_name", "gfx::timsort")
