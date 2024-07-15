from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class BitseryConan(ConanFile):
    name = "bitsery"
    description = (
        "Header only C++ binary serialization library. It is designed around "
        "the networking requirements for real-time data delivery, especially for games."
    )
    topics = ("serialization", "binary", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fraillt/bitsery"
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
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Bitsery")
        self.cpp_info.set_property("cmake_target_name", "Bitsery::bitsery")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Bitsery"
        self.cpp_info.names["cmake_find_package_multi"] = "Bitsery"
        self.cpp_info.components["bitserylib"].names["cmake_find_package"] = "bitsery"
        self.cpp_info.components["bitserylib"].names["cmake_find_package_multi"] = "bitsery"
        self.cpp_info.components["bitserylib"].set_property("cmake_target_name", "Bitsery::bitsery")
        self.cpp_info.components["bitserylib"].bindirs = []
        self.cpp_info.components["bitserylib"].libdirs = []
