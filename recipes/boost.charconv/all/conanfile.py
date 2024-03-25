from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.50.0"

class BoostCharConvConan(ConanFile):
    name = "charconv"
    description = "C++11 compatible implementation of <charconv>."
    license = "BSL-1.0"
    topics = ("conversion", "from_chars", "charconv")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cppalliance/charconv"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    # no_copy_source = True

    # def package_id(self):
    #     self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        # basic_layout(self, src_folder="src")
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    # def package(self):
    #     copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
    #     copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package(self):
        copy(self, pattern="*LICENSE.rst", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CharConv")
        self.cpp_info.set_property("cmake_target_name", "CharConv::charconv")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "CharConv"
        self.cpp_info.names["cmake_find_package_multi"] = "CharConv"
        self.cpp_info.components["charconv"].names["cmake_find_package"] = "charconv"
        self.cpp_info.components["charconv"].names["cmake_find_package_multi"] = "charconv"
        self.cpp_info.components["charconv"].set_property("cmake_target_name", "CharConv::charconv")
