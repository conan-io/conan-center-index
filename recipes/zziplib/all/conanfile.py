from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class ZziplibConan(ConanFile):
    name = "zziplib"
    description = "The ZZIPlib provides read access on ZIP-archives and unpacked data"
    topics = ("zip", "archive", "decompression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gdraheim/zziplib"
    license = "GPL-2.0-or-later"

    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "zzipmapped": [True, False],
        "zzipfseeko": [True, False],
        "zzipwrap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zzipmapped": True,
        "zzipfseeko": True,
        "zzipwrap": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        # Old versions do not support llvm >= 15
        if (Version(self.version) < "0.13.78"
                and self.settings.compiler in ("clang", "apple-clang")
                and Version(self.settings.compiler.version) >= "15.0"):
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.compiler} >= 15 due to incompatible pointer to integer conversion errors")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Older versions had BUILD_STATIC_LIBS option, new ones only have BUILD_SHARED_LIBS
        if Version(self.version) < "0.13.78":
            tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        else:
            # Disable sanitizer for newer versions
            tc.variables["FORTIFY"] = False
        tc.variables["ZZIPCOMPAT"] = self.settings.os != "Windows"
        tc.variables["ZZIPMMAPPED"] = self.options.zzipmapped
        tc.variables["ZZIPFSEEKO"] = self.options.zzipfseeko
        tc.variables["ZZIPWRAP"] = self.options.zzipwrap
        tc.variables["ZZIPSDL"] = False
        tc.variables["ZZIPBINS"] = False
        tc.variables["ZZIPTEST"] = False
        tc.variables["ZZIPDOCS"] = False
        # For msvc shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.LIB", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "zziplib-all-do-not-use")

        suffix = ""
        if self.settings.build_type == "Release" and \
           (not self.options.shared or self.settings.os == "Windows" or is_apple_os(self)):
            suffix += f"-{Version(self.version).major}"

        # libzzip
        self.cpp_info.components["zzip"].set_property("pkg_config_name", "zziplib")
        self.cpp_info.components["zzip"].libs = [f"zzip{suffix}"]
        self.cpp_info.components["zzip"].requires = ["zlib::zlib"]
        # libzzipmmapped
        if self.options.zzipmapped:
            self.cpp_info.components["zzipmmapped"].set_property("pkg_config_name", "zzipmmapped")
            if Version(self.version) >= "0.13.72" and self.options.shared and is_apple_os(self):
                self.cpp_info.components["zzipmmapped"].libs = [f"zzipmmapped"]
            else:
                self.cpp_info.components["zzipmmapped"].libs = [f"zzipmmapped{suffix}"]
            self.cpp_info.components["zzipmmapped"].requires = ["zlib::zlib"]
        # libzzipfseeko
        if self.options.zzipfseeko:
            self.cpp_info.components["zzipfseeko"].set_property("pkg_config_name", "zzipfseeko")
            if Version(self.version) >= "0.13.72" and self.options.shared and is_apple_os(self):
                self.cpp_info.components["zzipfseeko"].libs = [f"zzipfseeko"]
            else:
                self.cpp_info.components["zzipfseeko"].libs = [f"zzipfseeko{suffix}"]
            self.cpp_info.components["zzipfseeko"].requires = ["zlib::zlib"]
        # libzzipwrap
        if self.options.zzipwrap:
            self.cpp_info.components["zzipwrap"].set_property("pkg_config_name", "zzipwrap")
            self.cpp_info.components["zzipwrap"].libs = [f"zzipwrap{suffix}"]
            self.cpp_info.components["zzipwrap"].requires = ["zzip", "zlib::zlib"]
