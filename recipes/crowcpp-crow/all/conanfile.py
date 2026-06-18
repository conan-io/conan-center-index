from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.1"

class CrowConan(ConanFile):
    name = "crowcpp-crow"
    description = "Crow is a C++ microframework for running web services."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://crowcpp.org/"
    topics = ("web", "microframework", "header-only")
    package_type = "header-library"
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "amalgamation": [True, False],
        "with_ssl": [True, False],
        "with_compression": [True, False],
    }
    default_options = {
        "amalgamation": False,
        "with_ssl": False,
        "with_compression": False,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("asio/1.29.0", transitive_headers=True)
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <3]")
        if self.options.with_compression:
            self.requires("zlib/[>=1.2.11 <2]")

    def package_id(self):
        self.info.settings.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.amalgamation:
            tc = CMakeToolchain(self)
            tc.cache_variables["CROW_BUILD_EXAMPLES"] = False
            tc.cache_variables["CROW_BUILD_TESTS"] = False
            tc.cache_variables["CROW_AMALGAMATE"] = True
            tc.generate()

    def build(self):
        if self.options.amalgamation:
            cmake = CMake(self)
            cmake.configure()
            cmake.build(target="crow_amalgamated")


    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        if self.options.amalgamation:
            copy(
                self,
                pattern="crow_all.h",
                dst=os.path.join(self.package_folder, "include"),
                src=self.build_folder,
            )
        else:
            copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"),
            )
            copy(
                self,
                pattern="*.hpp",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"),
            )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.requires.append("asio::asio")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["wsock32", "ws2_32"]

        self.cpp_info.set_property("cmake_file_name", "Crow")
        self.cpp_info.set_property("cmake_target_name", "Crow::Crow")

        if self.options.with_ssl:
            self.cpp_info.defines.append("CROW_ENABLE_SSL")
            self.cpp_info.requires.append("openssl::ssl")
        if self.options.with_compression:
            self.cpp_info.defines.append("CROW_ENABLE_COMPRESSION")
            self.cpp_info.requires.append("zlib::zlib")
