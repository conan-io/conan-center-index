import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class Re2CConan(ConanFile):
    name = "re2c"
    description = "re2c is a free and open-source lexer generator for C/C++, Go and Rust."
    license = "LicenseRef-re2c"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://re2c.org/"
    topics = ("lexer", "language", "tokenizer", "flex")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["RE2C_REBUILD_DOCS"] = False
        tc.cache_variables["RE2C_BUILD_BENCHMARKS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)
        copy(self, "NO_WARRANTY",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)
        copy(self, "*.re",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"),
             keep_path=False)

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        include_dir = os.path.join(self.package_folder, "include")
        self.buildenv_info.define("RE2C_STDLIB_DIR", include_dir)
