import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd


class HicalConan(ConanFile):
    name = "hical"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Hical61/Hical"
    description = "Modern C++20/C++26 high-performance web framework based on Boost.Asio/Beast"
    topics = ("web-framework", "http", "websocket", "boost-asio", "coroutine", "cpp20", "cpp26")
    package_type = "static-library"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "with_reflection": [True, False],
        "with_database": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_reflection": False,
        "with_database": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        check_min_cppstd(self, 20)
        if self.options.with_reflection:
            check_min_cppstd(self, 26)

    def requirements(self):
        self.requires("boost/[>=1.82.0]", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1.0]", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["HICAL_BUILD_TESTS"] = False
        tc.variables["HICAL_BUILD_EXAMPLES"] = False
        tc.variables["HICAL_ENABLE_REFLECTION"] = bool(self.options.with_reflection)
        tc.variables["HICAL_WITH_DATABASE"] = bool(self.options.with_database)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hical")
        self.cpp_info.set_property("cmake_target_name", "hical::hical_core")

        self.cpp_info.libs = ["hical_core"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "mswsock"])

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
