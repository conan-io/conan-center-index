import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class PocketfftConan(ConanFile):
    name = "pocketfft"
    description = "PocketFFT: a heavily modified implementation of FFTPack"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mreineck/pocketfft"
    topics = ("fft", "fast-fourier-transform", "fftpack", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "cache_size": ["ANY"],
        "multithreading": [True, False],
        "pthread": [True, False],
        "vectorization": [True, False],
    }
    default_options = {
        "cache_size": 0,
        "multithreading": True,
        "pthread": False,
        "vectorization": True,
    }

    def configure(self):
        if not self.options.multithreading:
            del self.options.pthread

    def requirements(self):
        if self.options.get_safe("pthread") and self.settings.os == "Windows":
            self.requires("pthreads4w/3.0.0")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        if not str(self.options.cache_size).isdigit() or int(str(self.options.cache_size)) < 0:
            raise ConanInvalidConfiguration("cache_size option must be greater or equal to 0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.defines.append(f"POCKETFFT_CACHE_SIZE={self.options.cache_size}")
        if not self.options.multithreading:
            self.cpp_info.defines.append("POCKETFFT_NO_MULTITHREADING")
        if self.options.get_safe("pthread"):
            self.cpp_info.defines.append("POCKETFFT_PTHREADS")
        if not self.options.vectorization:
            self.cpp_info.defines.append("POCKETFFT_NO_VECTORS")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.multithreading:
                self.cpp_info.system_libs.append("pthread")

        if self.options.get_safe("pthread") and self.settings.os == "Windows":
            self.cpp_info.system_libs.append("pthreads4w::pthreads4w")
