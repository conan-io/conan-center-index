import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class SleefConan(ConanFile):
    name = "sleef"
    description = "SLEEF is a library that implements vectorized versions of C standard math functions."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sleef.org"
    topics = ("vectorization", "simd")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "shared sleef not supported on Windows, it produces runtime errors"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["BUILD_STATIC_TEST_BINS"] = False
        tc.cache_variables["ENABLE_LTO"] = False
        tc.cache_variables["BUILD_LIBM"] = True
        tc.cache_variables["BUILD_DFT"] = False
        tc.cache_variables["BUILD_QUAD"] = False
        tc.cache_variables["BUILD_GNUABI_LIBS"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["BUILD_INLINE_HEADERS"] = False
        tc.cache_variables["SLEEF_TEST_ALL_IUT"] = False
        tc.cache_variables["SLEEF_SHOW_CONFIG"] = True
        tc.cache_variables["SLEEF_SHOW_ERROR_LOG"] = False
        tc.cache_variables["ENFORCE_TESTER"] = False
        tc.cache_variables["ENFORCE_TESTER3"] = False
        tc.cache_variables["ENABLE_ALTDIV"] = False
        tc.cache_variables["ENABLE_ALTSQRT"] = False
        tc.cache_variables["DISABLE_FFTW"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sleef")
        self.cpp_info.libs = ["sleef"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines = ["SLEEF_STATIC_LIBS"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
