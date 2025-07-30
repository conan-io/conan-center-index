from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class MinizipNgConan(ConanFile):
    name = "minizip-ng"
    description = "Fork of the popular zip manipulation library found in the zlib distribution."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zlib-ng/minizip-ng"
    topics = ("compression", "zip")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "mz_compatibility": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
        "with_openssl": [True, False],
        "with_iconv": [True, False],
        "with_libbsd": [True, False],
        "with_libcomp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "mz_compatibility": False,
        "with_zlib": True,
        "with_bzip2": True,
        "with_lzma": True,
        "with_zstd": True,
        "with_openssl": True,
        "with_iconv": True,
        "with_libbsd": True,
        "with_libcomp": True,
    }

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_iconv
            del self.options.with_libbsd
        if not is_apple_os(self):
            del self.options.with_libcomp

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.get_safe("with_libcomp"):
            del self.options.with_zlib

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_bzip2:
            self.requires("bzip2/[>=1.0.8 <2]")
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4.5 <6]")
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5.5 <2]")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.settings.os != "Windows":
            if self.options.get_safe("with_iconv"):
                self.requires("libiconv/1.17")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MZ_FETCH_LIBS"] = False
        tc.cache_variables["MZ_COMPAT"] = self.options.mz_compatibility
        tc.cache_variables["MZ_ZLIB"] = self.options.get_safe("with_zlib", False)
        tc.cache_variables["MZ_BZIP2"] = self.options.with_bzip2
        tc.cache_variables["MZ_LZMA"] = self.options.with_lzma
        tc.cache_variables["MZ_ZSTD"] = self.options.with_zstd
        tc.cache_variables["MZ_OPENSSL"] = self.options.with_openssl
        tc.cache_variables["MZ_LIBCOMP"] = self.options.get_safe("with_libcomp", False)
        if self.settings.os != "Windows":
            tc.cache_variables["MZ_ICONV"] = self.options.with_iconv
            tc.cache_variables["MZ_LIBBSD"] = self.options.with_libbsd
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True

        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_PkgConfig"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "minizip")
        self.cpp_info.set_property("cmake_target_name", "MINIZIP::minizip")
        self.cpp_info.set_property("pkg_config_name", "minizip")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        suffix = "" if self.options.mz_compatibility else "-ng"
        self.cpp_info.components["minizip"].libs = [f"minizip{suffix}"]
        if self.options.with_lzma:
            self.cpp_info.components["minizip"].defines.append("HAVE_LZMA")
        if is_apple_os(self) and self.options.get_safe("with_libcomp"):
            self.cpp_info.components["minizip"].defines.append("HAVE_LIBCOMP")
            self.cpp_info.components["minizip"].system_libs.append("compression")
        if self.options.with_bzip2:
            self.cpp_info.components["minizip"].defines.append("HAVE_BZIP2")

        minizip_dir = "minizip" if self.options.mz_compatibility else "minizip-ng"
        self.cpp_info.components["minizip"].includedirs.append(os.path.join(self.package_folder, "include", minizip_dir))

        self.cpp_info.components["minizip"].set_property("cmake_target_name", "MINIZIP::minizip")
        self.cpp_info.components["minizip"].set_property("pkg_config_name", "minizip")
        if self.options.get_safe("with_zlib"):
            self.cpp_info.components["minizip"].requires.append("zlib::zlib")
        if self.options.with_bzip2:
            self.cpp_info.components["minizip"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["minizip"].requires.append("xz_utils::xz_utils")
        if self.options.with_zstd:
            self.cpp_info.components["minizip"].requires.append("zstd::zstd")
        if self.options.with_openssl:
            self.cpp_info.components["minizip"].requires.append("openssl::openssl")
        elif is_apple_os(self):
            self.cpp_info.components["minizip"].frameworks.extend(["CoreFoundation", "Security"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["minizip"].system_libs.append("crypt32")
        if self.settings.os != "Windows" and self.options.with_iconv:
            self.cpp_info.components["minizip"].requires.append("libiconv::libiconv")

