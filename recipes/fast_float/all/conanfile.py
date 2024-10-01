from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"

class FastFloatConan(ConanFile):
    name = "fast_float"
    description = "Fast and exact implementation of the C++ from_chars " \
                  "functions for float and double types."
    license = ("Apache-2.0", "MIT", "BSL-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fastfloat/fast_float"
    topics = ("conversion", "from_chars", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "FastFloat")
        self.cpp_info.set_property("cmake_target_name", "FastFloat::fast_float")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "FastFloat"
        self.cpp_info.names["cmake_find_package_multi"] = "FastFloat"
        self.cpp_info.components["fastfloat"].names["cmake_find_package"] = "fast_float"
        self.cpp_info.components["fastfloat"].names["cmake_find_package_multi"] = "fast_float"
        self.cpp_info.components["fastfloat"].set_property("cmake_target_name", "FastFloat::fast_float")
