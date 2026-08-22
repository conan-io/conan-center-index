from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.0.9"


class JsrlConan(ConanFile):
    name = "jsrl"
    description = "Json Serialization and Reading Library - A modern C++ JSON library with UTF-8 correctness, immutability, and high-fidelity numbers"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/adobe/jsrl"
    topics = ("json", "parser")

    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]
    languages = "C++"

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["JSRL_BUILD_TESTS"] = False
        tc.cache_variables["JSRL_INSTALL"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["jsrl"]
        if not self.options.shared:
            self.cpp_info.defines = ["JSRL_STATIC_DEFINE"]
        self.cpp_info.set_property("cmake_file_name", "jsrl")
        self.cpp_info.set_property("cmake_target_name", "jsrl::jsrl")
        self.cpp_info.set_property("pkg_config_name", "jsrl")
