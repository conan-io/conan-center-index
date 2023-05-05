from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


class StrongTypeConan(ConanFile):
    name = "strong_type"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rollbear/strong_type"
    description = "An additive strong typedef library for C++14/17/20"
    topics = ("cpp14", "cpp17", "strong_type")
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "strong_type")
        self.cpp_info.set_property(
            "cmake_target_name", "rollbear::strong_type")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "strong_type"
        self.cpp_info.filenames["cmake_find_package_multi"] = "strong_type"
        self.cpp_info.names["cmake_find_package"] = "rollbear"
        self.cpp_info.names["cmake_find_package_multi"] = "rollbear"
        self.cpp_info.components["strong_type"].names["cmake_find_package"] = "strong_type"
        self.cpp_info.components["strong_type"].names["cmake_find_package_multi"] = "strong_type"
        self.cpp_info.components["strong_type"].set_property(
            "cmake_target_name", "rollbear::strong_type")
        self.cpp_info.components["strong_type"].bindirs = []
        self.cpp_info.components["strong_type"].frameworkdirs = []
        self.cpp_info.components["strong_type"].libdirs = []
        self.cpp_info.components["strong_type"].resdirs = []
