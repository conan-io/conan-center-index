from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version

import os

required_conan_version = ">=1.53.0"

class SimdutfConan(ConanFile):
    name = "simdutf"
    description = "Unicode routines (UTF8, UTF16): billions of characters per second."
    license = ("Apache-2.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/simdutf/simdutf"
    topics = ("unicode", "transcoding", "neon", "simd", "avx2", "sse2", "utf8", "utf16", )
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9.0":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc < 9.")
        if self.settings.compiler == "gcc" and self.settings.build_type == "Debug" and \
            Version(self.settings.compiler.version) < "10.0":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc < 10 with debug build")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SIMDUTF_BENCHMARKS"] = False
        tc.variables["SIMDUTF_TESTS"] = False
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) == "8":
            tc.variables["CMAKE_CXX_FLAGS"] = " -mavx512f"
        tc.variables["SIMDUTF_TOOLS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["simdutf"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
