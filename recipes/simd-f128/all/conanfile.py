from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class SimdF128Conan(ConanFile):
    name = "simd-f128"
    description = "128-bit Double-Double SIMD floating-point math library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tiw302.github.io/simd-f128/"
    topics = ("math", "simd", "double-double", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "simd_f128")
        self.cpp_info.set_property("cmake_target_name", "simd_f128::simd_f128")
