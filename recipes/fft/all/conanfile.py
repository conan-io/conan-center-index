import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class FftConan(ConanFile):
    name = "fft"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.kurims.kyoto-u.ac.jp/~ooura/fft.html"
    description = "This is a package to calculate Discrete Fourier/Cosine/Sine Transforms of 2,3-dimensional sequences of length 2^N."
    topics = ("conan", "fft", "fft2d", "fft3d", "dct", "dst", "dft")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "threads": [True, False],
               "max_threads": "ANY",
               "threads_begin_n": "ANY"}
    default_options = {"shared": False,
                       "fPIC": True,
                       "threads": False,
                       "max_threads": 4,
                       "threads_begin_n": 65536}
    exports_sources = ["CMakeLists.txt", "fft_build.c", "alloc.h.fixed", "fft.h", "fft2.h", "fft3.h", "dct.h"]
    generators = "cmake",

    @property
    def _build_subfolder(self):
        return "_build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)
        os.unlink("alloc.h")
        os.rename("alloc.h.fixed", "alloc.h")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if not self.options.threads:
            del self.options.max_threads
            del self.options.threads_begin_n
    
    def validate(self):
        def _is_power_of_two(n):
            return (n != 0) and (n & (n-1) == 0)

        if not self.options.max_threads.value.isdigit():
            raise ConanInvalidConfiguration("max_threads must be an integer")
        if not self.options.threads_begin_n.value.isdigit():
            raise ConanInvalidConfiguration("threads_begin_n must be an integer")
        if not _is_power_of_two(int(self.options.max_threads.value)):
            raise ConanInvalidConfiguration("max_threads must be a power of 2")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["THREADS"] = self.options.threads
        if self.options.threads:
            cmake.definitions["MAX_THREADS"] = self.options.max_threads
            cmake.definitions["THREADS_BEGIN_N"] = self.options.threads_begin_n
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"),
"""Copyright
    Copyright(C) 1997,2001 Takuya OOURA (email: ooura@kurims.kyoto-u.ac.jp).
    You may use, copy, modify this code for any purpose and 
    without fee. You may distribute this ORIGINAL package.""")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fft"]
        if not self.options.shared:
            self.cpp_info.defines.append("FFT_STATIC_DEFINE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.threads:
                self.cpp_info.system_libs.append("pthread")
