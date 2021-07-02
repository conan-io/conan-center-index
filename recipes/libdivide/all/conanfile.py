from conans import ConanFile, tools
import os


class LibdivideConan(ConanFile):
    name = "libdivide"
    description = "Header-only C/C++ library for optimizing integer division."
    topics = ("conan", "libdivide", "division", "integer")
    license = ["Zlib", "BSL-1.0"]
    homepage = "http://libdivide.com/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "arch", "compiler"
    no_copy_source = True
    options = {
        "simd_intrinsics": [False, "sse2", "avx2", "avx512"]
    }
    default_options = {
        "simd_intrinsics": False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.simd_intrinsics

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("libdivide.h", dst="include", src=self._source_subfolder)

    def package_info(self):
        simd = self.options.get_safe("simd_intrinsics", False)
        if bool(simd):
            self.cpp_info.defines = [
                {"sse2": "LIBDIVIDE_SSE2",
                 "avx2": "LIBDIVIDE_AVX2",
                 "avx512": "LIBDIVIDE_AVX512"}[str(simd)]
            ]
