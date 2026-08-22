import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import cross_building

required_conan_version = ">=2.18"


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
    implements = ["auto_shared_fpic"]
    languages = "C", "C++"

    @property
    def _support_gnulibs(self):
        return self.settings.os in ("Linux", "FreeBSD")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(
                "sleef on Windows is only supported for x86_64 architecture. See compatibility table https://github.com/shibatch/sleef#test-matrix"
            )
        if cross_building(self):
            # Fails with "No rule to make target `/bin/mkrename'"
            raise ConanInvalidConfiguration(f"{self.ref} does not support cross-building")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SLEEF_BUILD_LIBM"] = True
        tc.cache_variables["SLEEF_BUILD_DFT"] = False
        tc.cache_variables["SLEEF_BUILD_QUAD"] = True
        tc.cache_variables["SLEEF_BUILD_GNUABI_LIBS"] = self._support_gnulibs
        tc.cache_variables["SLEEF_BUILD_TESTS"] = False
        tc.cache_variables["SLEEF_SHOW_CONFIG"] = True
        tc.cache_variables["SLEEF_DISABLE_FFTW"] = True
        tc.cache_variables["SLEEF_DISABLE_MPFR"] = True
        tc.cache_variables["SLEEF_DISABLE_SVE"] = True
        tc.cache_variables["SLEEF_DISABLE_SSL"] = True
        tc.cache_variables["SLEEF_ENABLE_CUDA"] = False
        tc.cache_variables["SLEEF_ENABLE_TLFLOAT"] = False
        tc.cache_variables["SLEEF_ENABLE_TESTER4"] = False
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
        self.cpp_info.set_property("pkg_config_name", "none")
        self.cpp_info.set_property("cmake_file_name", "sleef")

        self.cpp_info.components["sleef"].libs = ["sleef"]
        self.cpp_info.components["sleef"].set_property("cmake_target_name", "sleef::sleef")
        self.cpp_info.components["sleef"].set_property("pkg_config_name", "sleef")

        self.cpp_info.components["sleefquad"].libs = ["sleefquad"]
        self.cpp_info.components["sleefquad"].set_property("cmake_target_name", "sleef::sleefquad")

        if self._support_gnulibs:
            self.cpp_info.components["sleef"].system_libs = ["m"]
            self.cpp_info.components["sleefgnuabi"].libs = ["sleefgnuabi"]
            self.cpp_info.components["sleefgnuabi"].set_property("cmake_target_name", "sleef::sleefgnuabi")
            self.cpp_info.components["sleefgnuabi"].system_libs = ["m"]

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.components["sleef"].defines = ["SLEEF_STATIC_LIBS"]
            self.cpp_info.components["sleefquad"].defines = ["SLEEF_STATIC_LIBS"]
