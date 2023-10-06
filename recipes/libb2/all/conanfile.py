import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.53.0"


class libb2Conan(ConanFile):
    name = "libb2"
    description = (
        "libb2 is a library that implements the BLAKE2 cryptographic hash function, which is faster than MD5, "
        "SHA-1, SHA-2, and SHA-3, yet is at least as secure as the latest standard SHA-3"
    )
    license = ["CC0-1.0", "OpenSSL", "APSL-2.0"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BLAKE2/BLAKE2"
    topics = ("blake2", "hash")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_sse": [True, False],
        "use_neon": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse": False,
        "use_neon": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.options.use_neon and not "arm" in self.settings.arch:
            raise ConanInvalidConfiguration("Neon sources only supported on arm-based CPUs")
        if self.options.use_neon and self.options.use_sse:
            raise ConanInvalidConfiguration("Neon and SSE can not be used together.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_SSE"] = self.options.use_sse
        tc.variables["USE_NEON"] = self.options.use_neon
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.export_sources_folder)
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["b2"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "libb2")]
