from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.1"


class NekoLogConan(ConanFile):
    name = "neko-log"
    license = "MIT OR Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/moehoshio/NekoLog"
    description = "An easy-to-use, modern, lightweight, and efficient C++20 logging library"
    topics = ("logging", "cpp20", "header-only", "async")

    package_type = "header-library"
    implements = "auto_header_only"

    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires("neko-schema/1.1.5", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        # Download sources from GitHub using conandata.yml
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NEKO_LOG_BUILD_TESTS"] = False
        tc.variables["NEKO_LOG_USE_MODULES"] = False  # Disable modules for compatibility
        tc.variables["NEKO_LOG_AUTO_FETCH_DEPS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "NekoLog")
        self.cpp_info.set_property("cmake_target_name", "Neko::Log")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
