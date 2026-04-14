from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm
import os


required_conan_version = ">=2.4"

# mirror
class ZycoreConan(ConanFile):
    name = "zycore"
    description = "Platform independent types, macros and a fallback for environments without LibC"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zyantific/zycore-c"
    topics = ("platform-independent", "types", "no-libc")
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
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.cache_variables["ZYCORE_BUILD_SHARED_LIB"] = self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*", excludes="zycore-config.cmake", folder=os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["Zycore"]
        self.cpp_info.set_property("cmake_target_name", "Zycore::Zycore")
        self.cpp_info.set_property("cmake_target_aliases", ["Zycore"])
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "zycore", "zyan-functions.cmake")])

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared:
            self.cpp_info.defines = ["ZYCORE_STATIC_BUILD"]
