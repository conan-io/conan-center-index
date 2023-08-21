import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibdivideConan(ConanFile):
    name = "libdivide"
    description = "Header-only C/C++ library for optimizing integer division."
    license = ["Zlib", "BSL-1.0"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libdivide.com/"
    topics = ("libdivide", "division", "integer", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "simd_intrinsics": [False, "sse2", "avx2", "avx512"],
        "sse2": [True, False],
        "avx2": [True, False],
        "avx512": [True, False],
        "neon": [True, False],
    }
    default_options = {
        "simd_intrinsics": False,
        "sse2": False,
        "avx2": False,
        "avx512": False,
        "neon": False,
    }
    no_copy_source = True

    def config_options(self):
        if Version(self.version) < "4.0.0":
            self.options.rm_safe("sse2")
            self.options.rm_safe("avx2")
            self.options.rm_safe("avx512")
            self.options.rm_safe("neon")
            if self.settings.arch not in ["x86", "x86_64"]:
                self.options.rm_safe("simd_intrinsics")
        else:
            self.options.rm_safe("simd_intrinsics")
            if self.settings.arch not in ["x86", "x86_64"]:
                self.options.rm_safe("sse2")
                self.options.rm_safe("avx2")
                self.options.rm_safe("avx512")
            if not str(self.settings.arch).startswith("arm"):
                self.options.rm_safe("neon")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if Version(self.version) < "4.0.0" and self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "libdivide.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "constant_fast_div.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "s16_ldparams.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "u16_ldparams.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        simd = self.options.get_safe("simd_intrinsics", False)
        if bool(simd):
            self.cpp_info.defines = [{"sse2": "LIBDIVIDE_SSE2", "avx2": "LIBDIVIDE_AVX2", "avx512": "LIBDIVIDE_AVX512"}[str(simd)]]
        if self.options.get_safe("sse2", False):
            self.cpp_info.defines.append("LIBDIVIDE_SSE2")
        if self.options.get_safe("avx2", False):
            self.cpp_info.defines.append("LIBDIVIDE_AVX2")
        if self.options.get_safe("avx512", False):
            self.cpp_info.defines.append("LIBDIVIDE_AVX512")
        if self.options.get_safe("neon", False):
            self.cpp_info.defines.append("LIBDIVIDE_NEON")
