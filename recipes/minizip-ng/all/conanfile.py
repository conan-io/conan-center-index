from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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

    @property
    def _needs_pkg_config(self):
        return self.options.with_lzma or self.options.with_zstd or self.options.with_openssl

    def export_sources(self):
        export_conandata_patches(self)

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
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.5")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.settings.os != "Windows":
            if self.options.get_safe("with_iconv"):
                self.requires("libiconv/1.17")

    def build_requirements(self):
        if self._needs_pkg_config:
            self.tool_requires("pkgconf/2.1.0")
        if Version(self.version) >= "4.0.0":
            self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self._needs_pkg_config:
            env = VirtualBuildEnv(self)
            env.generate()

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
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        if self._needs_pkg_config:
            deps = PkgConfigDeps(self)
            deps.generate()
            # TODO: to remove when properly handled by conan (see https://github.com/conan-io/conan/issues/11962)
            env = Environment()
            env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
            env.vars(self).save_script("conanbuild_pkg_config_path")

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "4.0.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                  "set_target_properties(${PROJECT_NAME} PROPERTIES POSITION_INDEPENDENT_CODE 1)",
                                  "")
        elif Version(self.version) == "4.0.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                  "set_target_properties(${MINIZIP_TARGET} PROPERTIES POSITION_INDEPENDENT_CODE 1)",
                                  "")

    def build(self):
        self._patch_sources()
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
        prefix = "lib" if is_msvc(self) or self._is_clang_cl else ""
        suffix = "" if self.options.mz_compatibility else "-ng"
        self.cpp_info.components["minizip"].libs = [f"{prefix}minizip{suffix}"]
        if self.options.with_lzma:
            self.cpp_info.components["minizip"].defines.append("HAVE_LZMA")
        if is_apple_os(self) and self.options.get_safe("with_libcomp"):
            self.cpp_info.components["minizip"].defines.append("HAVE_LIBCOMP")
        if self.options.with_bzip2:
            self.cpp_info.components["minizip"].defines.append("HAVE_BZIP2")

        if Version(self.version) >= "4.0.0":
            minizip_dir = "minizip" if self.options.mz_compatibility else "minizip-ng"
            self.cpp_info.components["minizip"].includedirs.append(os.path.join(self.package_folder, "include", minizip_dir))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "minizip"
        self.cpp_info.filenames["cmake_find_package_multi"] = "minizip"
        self.cpp_info.names["cmake_find_package"] = "MINIZIP"
        self.cpp_info.names["cmake_find_package_multi"] = "MINIZIP"
        self.cpp_info.components["minizip"].names["cmake_find_package"] = "minizip"
        self.cpp_info.components["minizip"].names["cmake_find_package_multi"] = "minizip"
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

