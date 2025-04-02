from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.0.9"



class PackageConan(ConanFile):
    name = "msgpack23"
    description = "A modern, header-only C++ library for MessagePack serialization and deserialization."
    license = "MIT"
    url = "https://github.com/rwindegger/msgpack23"
    homepage = "https://github.com/rwindegger/msgpack23"
    topics = ("msgpack", "serialization", "MessagePack")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 23)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.28 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        self.info.clear()

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.set_property("cmake_file_name", "msgpack23")
        self.cpp_info.set_property("cmake_target_name", "msgpack23::msgpack23")
