from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class JSONCConan(ConanFile):
    name = "json-c"
    description = "A JSON implementation in C"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/json-c/json-c"
    topics = ("json", "encoding", "decoding", "manipulation")

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
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "0.15":
            tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
            tc.variables["DISABLE_STATIC_FPIC"] = not self.options.get_safe("fPIC", True)
        tc.cache_variables["BUILD_TESTING"] = False
        if Version(self.version) < "0.17":
            # To install relocatable shared libs on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        else:
            tc.cache_variables["BUILD_APPS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["json-c"]

        self.cpp_info.set_property("cmake_file_name", "json-c")
        self.cpp_info.set_property("cmake_target_name", "json-c::json-c")
        self.cpp_info.set_property("pkg_config_name", "json-c")
        self.cpp_info.includedirs = ["include", os.path.join("include", "json-c")]

        if Version(self.version) >= "0.17" and self.settings.os in ["Linux", "FreeBSD", "Neutrino"]:
            self.cpp_info.system_libs.extend(["m",])
