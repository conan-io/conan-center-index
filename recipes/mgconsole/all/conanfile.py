from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd

import os


class Mgconsole(ConanFile):
    name = "mgconsole"
    description = "mgconsole is a command-line interface (CLI) used to interact with Memgraph from any terminal or operating system."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/memgraph/mgconsole"
    topics = ("mgconsole", "memgraph")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
            "build_tests": [True, False],
            }

    default_options = {
            "build_tests": False,
            }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("gflags/2.2.2")
        self.requires("mgclient/1.4.3")
        self.requires("replxx/0.0.4")
        self.requires("openssl/3.5.1")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = self.options.build_tests
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def validate(self):
        check_min_cppstd(self, 17)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
