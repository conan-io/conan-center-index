from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class ExpectedLiteConan(ConanFile):
    name = "expected-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/expected-lite"
    description = "expected lite - Expected objects in C++11 and later in a single-file header-only library"
    topics = ("cpp11", "cpp14", "cpp17", "expected", "expected-implementations")
    license = "BSL-1.0"
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
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "expected-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::expected-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "expected-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "expected-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["expectedlite"].names["cmake_find_package"] = "expected-lite"
        self.cpp_info.components["expectedlite"].names["cmake_find_package_multi"] = "expected-lite"
        self.cpp_info.components["expectedlite"].set_property("cmake_target_name", "nonstd::expected-lite")
