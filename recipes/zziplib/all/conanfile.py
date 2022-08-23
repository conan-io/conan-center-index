from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class ZziplibConan(ConanFile):
    name = "zziplib"
    description = "The ZZIPlib provides read access on ZIP-archives and unpacked data"
    topics = ("zip", "archive", "decompression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gdraheim/zziplib"
    license = "GPL-2.0-or-later"

    settings = "os", "arch", "compiler", "build_type"
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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

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

    def requirements(self):
        self.requires("zlib/1.2.12")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
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

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "zziplib-all-do-not-use")

        suffix = f"-{Version(self.version).major}" if self.settings.build_type == "Release" else ""

        # libzzip
        self.cpp_info.components["zzip"].set_property("pkg_config_name", "zziplib")
        self.cpp_info.components["zzip"].libs = [f"zzip{suffix}"]
        self.cpp_info.components["zzip"].requires = ["zlib::zlib"]
        # libzzipmmapped
        if self.options.zzipmapped:
            self.cpp_info.components["zzipmmapped"].set_property("pkg_config_name", "zzipmmapped")
            self.cpp_info.components["zzipmmapped"].libs = [f"zzipmmapped{suffix}"]
            self.cpp_info.components["zzipmmapped"].requires = ["zlib::zlib"]
        # libzzipfseeko
        if self.options.zzipfseeko:
            self.cpp_info.components["zzipfseeko"].set_property("pkg_config_name", "zzipfseeko")
            self.cpp_info.components["zzipfseeko"].libs = [f"zzipfseeko{suffix}"]
            self.cpp_info.components["zzipfseeko"].requires = ["zlib::zlib"]
        # libzzipwrap
        if self.options.zzipwrap:
            self.cpp_info.components["zzipwrap"].set_property("pkg_config_name", "zzipwrap")
            self.cpp_info.components["zzipwrap"].libs = [f"zzipwrap{suffix}"]
            self.cpp_info.components["zzipwrap"].requires = ["zzip", "zlib::zlib"]
