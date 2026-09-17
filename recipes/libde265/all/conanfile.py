from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
import os

required_conan_version = ">=2"


class Libde265Conan(ConanFile):
    name = "libde265"
    description = "Open h.265 video codec implementation."
    license = "LGPL-3.0-or-later"
    topics = ("codec", "video", "h.265")
    homepage = "https://github.com/strukturag/libde265"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd": [True, False],
        "avx2": [True, False],
        "avx512": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd": True,
        "avx2": True,
        "avx512": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch != "x86_64":
            del self.options.avx2
            del self.options.avx512

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.simd:
            self.options.rm_safe("avx2")
            self.options.rm_safe("avx512")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def validate_build(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.variables["ENABLE_SDL"] = False
        tc.variables["ENABLE_DECODER"] = False
        tc.variables["ENABLE_ENCODER"] = False
        tc.variables["ENABLE_SHERLOCK265"] = False
        tc.variables["ENABLE_SIMD"] = bool(self.options.simd)
        tc.variables["ENABLE_AVX2"] = bool(self.options.get_safe("avx2", False))
        tc.variables["ENABLE_AVX512"] = bool(self.options.get_safe("avx512", False))
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libde265")
        self.cpp_info.set_property("cmake_target_name", "de265")
        self.cpp_info.set_property("cmake_target_aliases", ["libde265"])
        self.cpp_info.set_property("pkg_config_name", "libde265")
        prefix = "lib" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}de265"]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBDE265_STATIC_BUILD"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
