import glob
import os
import shutil

from conan import ConanFile
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import replace_in_file, copy, get, rm, rmdir, save
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibjxlConan(ConanFile):
    name = "libjxl"
    description = "JPEG XL image format reference implementation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libjxl/libjxl"
    topics = ("image", "jpeg-xl", "jxl", "jpeg")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("brotli/1.1.0")
        if Version(self.version) >= "0.7":
            self.requires("highway/1.0.7")
        else:
            self.requires("highway/0.12.2")
        self.requires("lcms/2.14")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        if cross_building(self):
            tc.variables["CMAKE_SYSTEM_PROCESSOR"] = str(self.settings.arch)
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # Disable tools and extras
        save(self, os.path.join(self.source_folder, "tools", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "lib", "jxl_extras.cmake"), "")
        # Inject Conan dependencies
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory(third_party)",
                        ("find_package(lcms REQUIRED CONFIG)\n"
                         "find_package(brotli REQUIRED CONFIG)\n"
                         "find_package(highway REQUIRED CONFIG)\n"
                         "link_libraries(brotli::brotli highway::highway lcms::lcms)\n")
                        )
        # Do not link directly against libraries
        jxl_cmake = os.path.join(self.source_folder, "lib", "jxl.cmake")
        for lib, replacement in [
            ("hwy", "highway::highway"),
            ("brotlicommon-static", "brotli::brotli"),
            ("brotlienc-static", "brotli::brotli"),
            ("brotlidec-static", "brotli::brotli"),
            ("lcms2", "lcms::lcms"),
        ]:
            replace_in_file(self, jxl_cmake, lib, replacement)
        # Avoid "INTERFACE_LIBRARY targets may only have whitelisted properties" error with Conan v1
        replace_in_file(self, jxl_cmake, '"$<BUILD_INTERFACE:$<TARGET_PROPERTY', "# ", strict=False)
        replace_in_file(self, jxl_cmake, "$<TARGET_PROPERTY", "# ", strict=False)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.shared:
            libs_dir = os.path.join(self.package_folder, "lib")
            rm(self, "*.a", libs_dir, recursive=True)
            rm(self, "*-static.lib", libs_dir, recursive=True)

            if self.settings.os == "Windows":
                copy(self, "jxl_dec.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
                copy(self, "jxl_dec.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
                for dll_path in glob.glob(os.path.join(libs_dir, "*.dll")):
                    shutil.move(dll_path, os.path.join(self.package_folder, "bin", os.path.basename(dll_path)))
            else:
                copy(self, "libjxl_dec.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def _lib_name(self, name):
        if not self.options.shared and self.settings.os == "Windows":
            return name + "-static"
        return name

    def package_info(self):
        # jxl
        self.cpp_info.components["jxl"].set_property("pkg_config_name", "libjxl")
        self.cpp_info.components["jxl"].libs = [self._lib_name("jxl")]
        self.cpp_info.components["jxl"].requires = ["brotli::brotli", "highway::highway", "lcms::lcms"]
        # jxl_dec
        self.cpp_info.components["jxl_dec"].set_property("pkg_config_name", "libjxl_dec")
        self.cpp_info.components["jxl_dec"].libs = [self._lib_name("jxl_dec")]
        self.cpp_info.components["jxl_dec"].requires = ["brotli::brotli", "highway::highway", "lcms::lcms"]
        # jxl_threads
        self.cpp_info.components["jxl_threads"].set_property("pkg_config_name", "libjxl_threads")
        self.cpp_info.components["jxl_threads"].libs = [self._lib_name("jxl_threads")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["jxl_threads"].system_libs = ["pthread"]

        if not self.options.shared and stdcpp_library(self):
            self.cpp_info.components["jxl"].system_libs.append(stdcpp_library(self))
            self.cpp_info.components["jxl_dec"].system_libs.append(stdcpp_library(self))
            self.cpp_info.components["jxl_threads"].system_libs.append(stdcpp_library(self))
