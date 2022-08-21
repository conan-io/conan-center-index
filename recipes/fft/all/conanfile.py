from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, save
import os

required_conan_version = ">=1.47.0"


class FftConan(ConanFile):
    name = "fft"
    license = "LicenseRef-LICENSE"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.kurims.kyoto-u.ac.jp/~ooura/fft.html"
    description = (
        "This is a package to calculate Discrete Fourier/Cosine/Sine "
        "Transforms of 2,3-dimensional sequences of length 2^N."
    )
    topics = ("fft", "fft2d", "fft3d", "dct", "dst", "dft")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": [True, False],
        "max_threads": ["ANY"],
        "threads_begin_n": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": False,
        "max_threads": 4,
        "threads_begin_n": 65536,
    }

    exports_sources = ["CMakeLists.txt", "fft_build.c", "fft.h", "fft2.h", "fft3.h", "dct.h"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass
        if not self.options.threads:
            del self.options.max_threads
            del self.options.threads_begin_n

    def validate(self):
        def _is_power_of_two(n):
            return (n != 0) and (n & (n-1) == 0)

        if self.info.options.threads:
            if not self.info.options.max_threads.isdigit():
                raise ConanInvalidConfiguration("max_threads must be an integer")
            if not self.info.options.threads_begin_n.isdigit():
                raise ConanInvalidConfiguration("threads_begin_n must be an integer")
            if not _is_power_of_two(int(self.info.options.max_threads)):
                raise ConanInvalidConfiguration("max_threads must be a power of 2")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FFT_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["FFT_THREADS"] = self.options.threads
        if self.options.threads:
            tc.variables["FFT_MAX_THREADS"] = self.options.max_threads
            tc.variables["FFT_THREADS_BEGIN_N"] = self.options.threads_begin_n
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"),
"""Copyright
    Copyright(C) 1997,2001 Takuya OOURA (email: ooura@kurims.kyoto-u.ac.jp).
    You may use, copy, modify this code for any purpose and
    without fee. You may distribute this ORIGINAL package.""")
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fft"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threads:
                self.cpp_info.system_libs.append("pthread")
