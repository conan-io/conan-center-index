from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class CrowConan(ConanFile):
    name = "crowcpp-crow"
    description = "Crow is a C++ microframework for running web services."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://crowcpp.org/"
    topics = ("web", "microframework", "header-only")
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

    @property
    def _min_cppstd(self):
        return 11

    def configure(self):
        if Version(self.version) < "1.0":
            del self.options.with_ssl
            del self.options.with_compression

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "1.1.0":
            self.requires("boost/1.83.0")
        else:
            self.requires("asio/1.29.0", transitive_headers=True)
        if Version(self.version) >= "1.0":
            if self.options.with_ssl:
                self.requires("openssl/[>=1.1 <3]")
            if self.options.with_compression:
                self.requires("zlib/[>=1.2.11 <2]")

    def package_id(self):
        self.info.settings.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.amalgamation:
            tc = CMakeToolchain(self)
            if Version(self.version) < "1.0":
                tc.variables["BUILD_EXAMPLES"] = False
                tc.variables["BUILD_TESTING"] = False
            else:
                tc.variables["CROW_BUILD_EXAMPLES"] = False
                tc.variables["CROW_BUILD_TESTS"] = False
                tc.variables["CROW_AMALGAMATE"] = True
            tc.generate()

    def build(self):
        if self.options.amalgamation:
            cmake = CMake(self)
            cmake.configure()
            if Version(self.version) < "1.0":
                cmake.build(target="amalgamation")
            else:
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

        if Version(self.version) < "1.1.0":
            self.cpp_info.requires.append("boost::headers")
        else:
            self.cpp_info.requires.append("asio::asio")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]

        self.cpp_info.set_property("cmake_file_name", "Crow")
        self.cpp_info.set_property("cmake_target_name", "Crow::Crow")

        if Version(self.version) >= "1.0":
            if self.options.with_ssl:
                self.cpp_info.defines.append("CROW_ENABLE_SSL")
                self.cpp_info.requires.append("openssl::ssl")
            if self.options.with_compression:
                self.cpp_info.defines.append("CROW_ENABLE_COMPRESSION")
                self.cpp_info.requires.append("zlib::zlib")
