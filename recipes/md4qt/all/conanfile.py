from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.1"


class Md4QtConan(ConanFile):
    name = "md4qt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/md4qt"
    license = "MIT"
    description = "C++ library for parsing Markdown."
    topics = ("markdown", "gfm", "parser", "ast", "commonmark", "md", "qt6", "cpp17")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=6.8 <7]", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("qt/<host_version>")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_MD4QT_TESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "MIT.txt", src=os.path.join(self.source_folder, "LICENSES"), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["md4qt"]
