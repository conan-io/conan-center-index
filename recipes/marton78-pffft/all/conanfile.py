from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os

required_conan_version = ">=2.0.9"


class Marton78PffftConan(ConanFile):
    name = "marton78-pffft"
    description = ("Fork of Julien Pommier's PFFFT, a pretty fast FFT, adding double precision, "
                   "fast convolution and DSP helpers")
    license = "DocumentRef-LICENSE.txt:LicenseRef-marton78-pffft"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/marton78/pffft"
    topics = ("fft", "fft-library", "convolution", "fast-convolution", "dsp")
    package_type = "library"
    provides = "pffft"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd": [True, False],
        "with_float": [True, False],
        "with_double": [True, False],
        "with_pffastconv": [True, False],
        "with_pfdsp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd": True,
        "with_float": True,
        "with_double": True,
        "with_pffastconv": False,
        "with_pfdsp": False,
    }
    implements = ["auto_shared_fpic"]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # The public API is C. pfdsp is implemented in C++, with the C++ standard
        # fixed by upstream, so only the C++ runtime matters when it is packaged.
        self.settings.rm_safe("compiler.cppstd")
        if not self.options.with_pfdsp:
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if not self.options.with_float and not self.options.with_double:
            raise ConanInvalidConfiguration(f"{self.ref} requires at least one of 'with_float' or 'with_double'")
        # pffastconv and pfdsp only exist in single precision
        for opt in ("with_pffastconv", "with_pfdsp"):
            if self.options.get_safe(opt) and not self.options.with_float:
                raise ConanInvalidConfiguration(f"{self.ref} '{opt}' requires 'with_float'")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PFFFT_USE_TYPE_FLOAT"] = bool(self.options.with_float)
        tc.cache_variables["PFFFT_USE_TYPE_DOUBLE"] = bool(self.options.with_double)
        tc.cache_variables["PFFFT_USE_SIMD"] = bool(self.options.simd)
        tc.cache_variables["INSTALL_PFFFT"] = True
        tc.cache_variables["INSTALL_PFFASTCONV"] = bool(self.options.with_pffastconv)
        tc.cache_variables["INSTALL_PFDSP"] = bool(self.options.with_pfdsp)
        tc.cache_variables["PFFFT_BUILD_TESTS"] = False
        tc.cache_variables["PFFFT_BUILD_BENCHMARKS"] = False
        tc.cache_variables["PFFFT_BUILD_EXAMPLES"] = False
        # Only used by the benchmarks, don't pick them up from the system
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_PAPI"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_MIPP"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pffft")

        system_libs = ["m"] if self.settings.os in ["Linux", "FreeBSD"] else []

        pffft = self.cpp_info.components["pffft"]
        pffft.set_property("cmake_target_name", "PFFFT::PFFFT")
        pffft.libs = ["pffft"]
        pffft.system_libs = list(system_libs)
        if not self.options.shared:
            pffft.defines = ["PFFFT_STATIC_DEFINE"]

        if self.options.with_pffastconv:
            pffastconv = self.cpp_info.components["pffastconv"]
            pffastconv.set_property("cmake_target_name", "PFFFT::PFFASTCONV")
            pffastconv.libs = ["pffastconv"]
            pffastconv.requires = ["pffft"]
            pffastconv.system_libs = list(system_libs)
            if not self.options.shared:
                pffastconv.defines = ["PFFASTCONV_STATIC_DEFINE"]

        if self.options.with_pfdsp:
            pfdsp = self.cpp_info.components["pfdsp"]
            pfdsp.set_property("cmake_target_name", "PFFFT::PFDSP")
            pfdsp.libs = ["pfdsp"]
            pfdsp.system_libs = list(system_libs)
            if not self.options.shared:
                pfdsp.defines = ["PFDSP_STATIC_DEFINE"]
                libcxx = stdcpp_library(self)
                if libcxx:
                    pfdsp.system_libs.append(libcxx)
