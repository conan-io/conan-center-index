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
    license = ("Apache-2.0", "MIT")
    topics = ("fast_float", "conversion", "from_chars")
    homepage = "https://github.com/fastfloat/fast_float"
    url = "https://github.com/conan-io/conan-center-index"
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
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "FastFloat")
        self.cpp_info.set_property("cmake_target_name", "FastFloat::fast_float")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "FastFloat"
        self.cpp_info.names["cmake_find_package_multi"] = "FastFloat"
        self.cpp_info.components["fastfloat"].names["cmake_find_package"] = "fast_float"
        self.cpp_info.components["fastfloat"].names["cmake_find_package_multi"] = "fast_float"
        self.cpp_info.components["fastfloat"].set_property("cmake_target_name", "FastFloat::fast_float")
