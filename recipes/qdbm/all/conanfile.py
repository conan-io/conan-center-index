import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.53.0"


class QDBMConan(ConanFile):
    name = "qdbm"
    description = "QDBM is a library of routines for managing a database."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dbmx.net/qdbm/"
    topics = ("database", "db")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_pthread": [True, False],
        "with_iconv": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_pthread": True,
        "with_iconv": True,
        "with_zlib": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.rm_safe("with_pthread")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_iconv:
            self.requires("libiconv/1.17")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONAN_qdbm_VERSION"] = self.version
        tc.variables["MYICONV"] = self.options.with_iconv
        tc.variables["MYZLIB"] = self.options.with_zlib
        tc.variables["MYPTHREAD"] = self.options.get_safe("with_pthread", False)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.export_sources_folder)
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["qdbm"]
        if self.options.get_safe("with_pthread"):
            self.cpp_info.system_libs.append("pthread")
