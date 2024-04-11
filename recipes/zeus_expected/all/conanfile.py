from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.cmake import cmake_layout
import os

required_conan_version = ">=2.0"


class ZeusExpectedConan(ConanFile):
    name = "zeus_expected"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeus-cpp/expected"
    description = "Backporting std::expected to C++17."
    topics = ("cpp17", "expected")
    license = "MIT"

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zeus_expected")
        self.cpp_info.set_property("cmake_target_name", "zeus::expected")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

    def package_id(self):
        self.info.clear()
