from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class RobinHoodHashingConan(ConanFile):
    name = "robin-hood-hashing"
    description = "Faster and more efficient replacement for std::unordered_map / std::unordered_set"
    topics = ("robin-hood-hashing", "header-only", "containers")
    homepage = "https://github.com/martinus/robin-hood-hashing"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

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
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "robin_hood.h", src=os.path.join(self.source_folder, "src", "include"),
                                   dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "robin_hood")
        self.cpp_info.set_property("cmake_target_name", "robin_hood::robin_hood")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "robin_hood"
        self.cpp_info.names["cmake_find_package_multi"] = "robin_hood"
