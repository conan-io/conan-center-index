from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class LaszipConan(ConanFile):
    name = "laszip"
    description = "C++ library for lossless LiDAR compression."
    license = "LGPL-2.1"
    topics = ("laszip", "las", "laz", "lidar", "compression", "decompression")
    homepage = "https://github.com/LASzip/LASzip"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LASZIP_BUILD_STATIC"] = not self.options.shared
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        suffix = Version(self.version).major if self.settings.os == "Windows" else ""
        self.cpp_info.libs = [f"laszip{suffix}"]
        if self.options.shared:
            self.cpp_info.defines.append("LASZIP_DYN_LINK")
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
