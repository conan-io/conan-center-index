from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os

required_conan_version = ">=1.53.0"

class OpenJPH(ConanFile):
    name = "openjph"
    description = "Open-source implementation of JPEG2000 Part-15 (or JPH or HTJ2K)"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aous72/OpenJPH"
    topics = ("ht-j2k", "jpeg2000", "jp2", "openjph", "image", "multimedia", "format", "graphics")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_executables": [True, False],
        "with_tiff": [True, False],
        "with_stream_expand_tool": [True, False],
        "disable_simd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_executables": True,
        "with_tiff": True,
        "with_stream_expand_tool": False,
        "disable_simd": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_executables and self.options.with_tiff:
            self.requires("libtiff/4.6.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            required_cpp_version = 11
            if self.options.with_stream_expand_tool:
                required_conan_version = 14
            check_min_cppstd(self, required_cpp_version)

        if self.settings.compiler == "gcc" and \
            Version(self.settings.compiler.version) < "6.0":
            raise ConanInvalidConfiguration(f"{self.ref} requires gcc >= 6.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OJPH_BUILD_EXECUTABLES"] = self.options.with_executables
        tc.variables["OJPH_ENABLE_TIFF_SUPPORT"] = self.options.with_tiff
        tc.variables["OJPH_BUILD_STREAM_EXPAND"] = self.options.with_stream_expand_tool
        tc.variables["OJPH_DISABLE_SIMD"] = self.options.disable_simd

        # Workaround for Conan 1 where the CXX standard version isn't set to a fallback to gnu98 happens
        if not self.settings.get_safe("compiler.cppstd"):
            tc.cache_variables["CMAKE_CXX_STANDARD"] = 14 if self.options.with_stream_expand_tool else 11

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()

        cm = CMake(self)
        cm.configure()
        cm.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cm = CMake(self)
        cm.install()

        # Cleanup package own pkgconfig
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "openjph")
        self.cpp_info.set_property("cmake_target_name", "openjph::openjph")
        self.cpp_info.set_property("pkg_config_name", "openjph")

        version_suffix = ""
        if is_msvc(self):
            v = Version(self.version)
            version_suffix = f".{v.major}.{v.minor}"
        self.cpp_info.libs = ["openjph" + version_suffix]

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "openjph"
        self.cpp_info.names["cmake_find_package_multi"] = "openjph"
        self.cpp_info.names["pkg_config"] = "openjph"
