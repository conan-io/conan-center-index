from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os

required_conan_version = ">=2.4"


class SpeexDspConan(ConanFile):
    name = "speexdsp"
    description = "SpeexDSP is a patent-free, Open Source/Free Software DSP library derived from Speex."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.xiph.org/xiph/speexdsp"
    topics = ("speex", "dsp", "audio", "resampler", "echo-cancellation", "preprocessor")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fixed_point": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fixed_point": False,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_FIXED_POINT"] = self.options.fixed_point
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "Makefile.am", os.path.join(self.package_folder, "include"), recursive=True)
        rm(self, "*.h.in", os.path.join(self.package_folder, "include"), recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["speexdsp"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.append("m")
