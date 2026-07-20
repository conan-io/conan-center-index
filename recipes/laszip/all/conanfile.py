from conan import ConanFile
from conan.tools.build import stdcpp_library, check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class LaszipConan(ConanFile):
    name = "laszip"
    description = "C++ library for lossless LiDAR compression."
    license = "LGPL-2.1"
    topics = ("las", "laz", "lidar", "compression", "decompression")
    homepage = "https://github.com/LASzip/LASzip"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 14

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if Version(self.version) >= "3.4.4":
            self.license = "Apache-2.0"
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        # The license file was renamed from "COPYING" to "COPYING.txt" in 3.5.0
        license_file = "COPYING.txt" if Version(self.version) >= "3.5.0" else "COPYING"
        copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        suffix = Version(self.version).major if self.settings.os == "Windows" else ""
        self.cpp_info.libs = [f"laszip{suffix}"]
        if Version(self.version) >= "3.5.0":
            # Since 3.5.0, laszip_api.h only uses the installed include layout
            # (<laszip/laszip_common.h>) when LASZIP_API_VERSION is defined; otherwise
            # it falls back to the in-tree <laszip_common.h> which we do not ship.
            self.cpp_info.defines.append("LASZIP_API_VERSION")
        if self.options.shared:
            self.cpp_info.defines.append("LASZIP_DYN_LINK")
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
