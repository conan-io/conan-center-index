from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os


required_conan_version = ">=2.1"


class NekoThreadPoolConan(ConanFile):
    name = "neko-threadpool"
    license = "MIT OR Apache-2.0"
    homepage = "https://github.com/moehoshio/NekoThreadPool"
    url = "https://github.com/conan-io/conan-center-index"
    description = "An easy-to-use and efficient C++ 20 thread pool that supports task priorities and task submission to specific threads"
    topics = ("c++20", "header-only", "threadpool", "concurrency", "utilities")

    settings = "os", "compiler", "build_type", "arch"

    # Header-only library
    package_type = "header-library"
    implements = "auto_header_only"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("neko-schema/1.1.5", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NEKO_THREAD_POOL_BUILD_TESTS"] = False
        tc.variables["NEKO_THREAD_POOL_ENABLE_MODULE"] = False
        tc.variables["NEKO_THREAD_POOL_AUTO_FETCH_DEPS"] = False
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
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Set the CMake package file name to match the official CMake config
        self.cpp_info.set_property("cmake_file_name", "NekoThreadPool")

        # Main header-only target
        self.cpp_info.set_property("cmake_target_name", "Neko::ThreadPool")

        # Add pthread if needed in Linux/FreeBSD
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])
