from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
import os

required_conan_version = ">=2.1"

class PackageConan(ConanFile):
    name = "libobjc2"
    description = "Objective-C runtime library intended for use with Clang."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gnustep/libobjc2"
    topics = ("objective-c", "objective-c-plus-plus", "clang", "gnustep", "objective-c-runtime", "runtime-library")
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tsl-robin-map/[>=1.2.1 <2]")

    def validate(self):
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration("libobjc2 supports clang only.")

        if is_apple_os(self):
            raise ConanInvalidConfiguration("libobjc2 does not support macOS.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 17)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        # Prevent picking up a default install location through gnustep-config
        tc.cache_variables["GNUSTEP_INSTALL_TYPE"] = "NONE"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["objc"]
        self.cpp_info.set_property("pkg_config_name", "libobjc")
