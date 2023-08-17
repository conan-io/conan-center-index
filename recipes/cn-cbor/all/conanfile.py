import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class CnCborStackConan(ConanFile):
    name = "cn-cbor"
    description = "A constrained node implementation of CBOR in C"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jimsch/cn-cbor/"
    topics = ("cbor", "nodes", "messaging")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported right now")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.cache_variables["CN_CBOR_FATAL_WARNINGS"] = False
        tc.cache_variables["CN_CBOR_COVERALLS"] = False
        tc.cache_variables["CN_CBOR_BUILD_TESTS"] = False
        tc.cache_variables["CN_CBOR_BUILD_DOCS"] = False
        # For v1.0.0
        tc.cache_variables["fatal_warnings"] = False
        tc.cache_variables["coveralls"] = False
        tc.cache_variables["build_tests"] = False
        tc.cache_variables["build_docs"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        os.remove(os.path.join(self.package_folder, "README.md"))
        os.remove(os.path.join(self.package_folder, "LICENSE"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cn-cbor", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["cn-cbor"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
