import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd

required_conan_version = ">=2"

class LibsersiConan(ConanFile):
    name = "libsersi"
    homepage = "https://github.com/crhowell3/libsersi"
    description = "Modern C++ implementation of IEEE 1278.1a-1998"
    topics = ("dis", "ieee", "1278.1a-1998")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    implements = ["auto_shared_fpic"]

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "libsersi-api.cmake"),
                        "set(CMAKE_CXX_STANDARD 17)", "")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")

    def validate(self):
        check_min_cppstd(self, 14)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["sersi"]
        self.cpp_info.set_property("cmake_target_name", "libsersi::sersi")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
