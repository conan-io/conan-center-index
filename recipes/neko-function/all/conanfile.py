from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os


required_conan_version = ">=2.1"


class NekoFunctionConan(ConanFile):
    name = "neko-function"
    license = "MIT OR Apache-2.0"
    homepage = "https://github.com/moehoshio/NekoFunction"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A comprehensive modern C++ utility library that provides practical functions for common programming tasks."
    topics = ("cpp", "utility", "modern-cpp", "functions", "neko", "archive", "string", "hash", "sha256" , "uuid" ,"datetime", "iso8601", "module")
    package_type = "library"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "enable_archive": [True, False],
        "enable_hash": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],

    }
    default_options = {
        "enable_archive": False,
        "enable_hash": False,
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not (self.options.enable_hash or self.options.enable_archive):
            self.package_type = "header-library"
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")

    def requirements(self):
        self.requires("neko-schema/1.1.5", transitive_headers=True)
        if self.options.enable_hash:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.enable_archive:
            self.requires("minizip-ng/[>=4.0]")

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NEKO_FUNCTION_BUILD_TESTS"] = False
        tc.variables["NEKO_FUNCTION_ENABLE_MODULE"] = False
        tc.variables["NEKO_FUNCTION_ENABLE_HASH"] = self.options.enable_hash
        tc.variables["NEKO_FUNCTION_ENABLE_ARCHIVE"] = self.options.enable_archive
        tc.variables["NEKO_FUNCTION_AUTO_FETCH_DEPS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("neko-schema", "cmake_target_aliases", ["NekoSchema"])
        # Set the target name mapping for minizip-ng
        if self.options.enable_archive:
            deps.set_property("minizip-ng", "cmake_find_mode", "both")
            deps.set_property("minizip-ng", "cmake_file_name", "minizip-ng")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        if self.options.enable_hash or self.options.enable_archive:
            cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # Set the CMake package file name to match the official CMake config
        self.cpp_info.set_property("cmake_file_name", "NekoFunction")

        # Main target
        self.cpp_info.set_property("cmake_target_name", "Neko::Function")

        # Configure based on package type
        if self.options.enable_hash or self.options.enable_archive:
            # Library target with compiled code
            # Note: Library will be installed via cmake.install() in package()
            self.cpp_info.libs = ["NekoFunction"]

            # Add dependencies
            if self.options.enable_hash:
                self.cpp_info.defines.append("NEKO_FUNCTION_ENABLE_HASH")
                self.cpp_info.defines.append("NEKO_IMPORT_OPENSSL")

            if self.options.enable_archive:
                self.cpp_info.defines.append("NEKO_FUNCTION_ENABLE_ARCHIVE")
        else:
            # Header-only target - no libraries
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []

    def package_id(self):
        if self.package_type == "header-library":
            self.info.clear()
