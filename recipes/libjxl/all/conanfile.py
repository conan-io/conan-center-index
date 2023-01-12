from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.53.0"

class LibjxlConan(ConanFile):
    name = "libjxl"
    description = "JPEG XL image format reference implementation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libjxl/libjxl"
    topics = ("image", "jpeg-xl", "jxl", "jpeg")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

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
        self.requires("brotli/1.0.9")
        if Version(self.version) < "0.7.0":
            self.requires("highway/0.12.2")
        else:
            self.requires("highway/1.0.2")
        self.requires("lcms/2.14")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        highway = self.dependencies["highway"]
        if hasattr(highway, "options.shared") and not highway.options.shared and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref}:shared=True requires -o highway:shared=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["JPEGXL_STATIC"] = not self.options.shared
        tc.variables["JPEGXL_ENABLE_BENCHMARK"] = False
        tc.variables["JPEGXL_ENABLE_EXAMPLES"] = False
        tc.variables["JPEGXL_ENABLE_MANPAGES"] = False
        tc.variables["JPEGXL_ENABLE_SJPEG"] = False
        tc.variables["JPEGXL_ENABLE_OPENEXR"] = False
        tc.variables["JPEGXL_ENABLE_SKCMS"] = False
        tc.variables["JPEGXL_ENABLE_TCMALLOC"] = False
        tc.variables["JPEGXL_FORCE_SYSTEM_BROTLI"] = True
        tc.variables["JPEGXL_FORCE_SYSTEM_HWY"] = True
        tc.variables["JPEGXL_FORCE_SYSTEM_LCMS2"] = True
        if cross_building(self):
            tc.variables["CMAKE_SYSTEM_PROCESSOR"] = \
                str(self.settings.arch)
        tc.variables["JPEGXL_ENABLE_TOOLS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.shared:
            libs_dir = os.path.join(self.package_folder, "lib")
            rm(self, pattern="*.a", folder=libs_dir)
            rm(self, pattern="*-static.lib", folder=libs_dir)

    def _lib_name(self, name):
        if not self.options.shared and self.settings.os == "Windows":
            return name + "-static"
        return name

    def _stdcpp_library(self):
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx in ["libstdc++", "libstdc++11"]:
            return "stdc++"
        elif libcxx in ["libc++"]:
            return "c++"
        elif libcxx in ["c++_shared"]:
            return "c++_shared"
        elif libcxx in ["c++_static"]:
            return "c++_static"
        return None

    def package_info(self):
        # jxl
        self.cpp_info.components["jxl"].names["pkg_config"] = "libjxl"
        self.cpp_info.components["jxl"].libs = [self._lib_name("jxl")]
        self.cpp_info.components["jxl"].requires = ["brotli::brotli",
                                                    "highway::highway",
                                                    "lcms::lcms"]
        # jxl_dec
        # in shared build, install jxl only.
        # https://github.com/libjxl/libjxl/blob/v0.5.0/lib/jxl.cmake#L544-L546
        if not self.options.shared:
            self.cpp_info.components["jxl_dec"].names["pkg_config"] = "libjxl_dec"
            self.cpp_info.components["jxl_dec"].libs = [self._lib_name("jxl_dec")]
            self.cpp_info.components["jxl_dec"].requires = ["brotli::brotli",
                                                            "highway::highway",
                                                            "lcms::lcms"]
        # jxl_threads
        self.cpp_info.components["jxl_threads"].names["pkg_config"] = \
            "libjxl_threads"
        self.cpp_info.components["jxl_threads"].libs = \
            [self._lib_name("jxl_threads")]
        if self.settings.os == "Linux":
            self.cpp_info.components["jxl_threads"].system_libs = ["pthread"]

        if not self.options.shared and self._stdcpp_library():
            self.cpp_info.components["jxl"].system_libs.append(
                self._stdcpp_library())
            self.cpp_info.components["jxl_dec"].system_libs.append(
                self._stdcpp_library())
            self.cpp_info.components["jxl_threads"].system_libs.append(
                self._stdcpp_library())
