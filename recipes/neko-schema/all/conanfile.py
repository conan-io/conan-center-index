from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os


required_conan_version = ">=2.1"


class NekoSchemaConan(ConanFile):
    name = "neko-schema"
    license = "MIT OR Apache-2.0"
    homepage = "https://github.com/moehoshio/NekoSchema"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A lightweight C++20 header-only library providing fundamental type definitions and utilities for the Neko ecosystem"
    topics = ("c++20", "header-only", "schema", "types", "auto-srcLoc", "utilities")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt", "include/*", "cmake/*", "LICENSE", "README.md"

    package_type = "header-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        data = self.conan_data or {}
        sources = data.get("sources", {})

        # Use remote source when available; otherwise fall back to exported sources (local workflow)
        if self.version in sources:
            get(self, **sources[self.version], strip_root=True)
        else:
            copy(self, pattern="*", src=self.export_sources_folder, dst=self.source_folder)

    def validate(self):
        check_min_cppstd(self, 20)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NEKO_SCHEMA_BUILD_TESTS"] = False
        tc.variables["NEKO_SCHEMA_ENABLE_MODULE"] = False
        tc.variables["NEKO_SCHEMA_AUTO_FETCH_DEPS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Set the CMake package file name to match the official CMake config
        self.cpp_info.set_property("cmake_file_name", "NekoSchema")
        self.cpp_info.set_property("cmake_target_name", "NekoSchema")
        self.cpp_info.set_property("cmake_target_aliases", ["Neko::Schema"])

    def package_id(self):
        self.info.clear()