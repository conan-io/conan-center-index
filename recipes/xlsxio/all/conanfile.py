from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class XlsxioConan(ConanFile):
    name = "xlsxio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/brechtsanders/xlsxio"
    description = "Cross-platform C library for reading values from and writing values to .xlsx files."
    topics = ("xlsx",)
    license = "MIT"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC":[True, False],
        "shared": [True, False],
        "build_static": [True, False],
        "build_pc_files": [True, False],
        "build_tools": [True, False],
        "build_examples": [True, False],
        "with_libzip": [True, False],
        "with_minizip_ng": [True, False],
        "with_wide": [True, False],
        "build_documentation": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": True,
        "build_static": True,
        "build_pc_files": True,
        "build_tools": True,
        "build_examples": True,
        "with_libzip": False,
        "with_minizip_ng": False,
        "with_wide": False,
        "build_documentation": False,
    }
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.2.34":
            del self.options.with_minizip_ng

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libzip:
            self.requires("libzip/1.7.3")
        elif Version(self.version) >= "0.2.34" and self.options.with_minizip_ng :
            self.requires("minizip-ng/3.0.8")
        else:
            self.requires("minizip/1.2.12")
        self.requires("expat/2.4.9")
        if self.options.with_wide:
            self.options["expat"].char_type="ushort"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = VirtualBuildEnv(self)
        tc.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC"] = self.options.build_static
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_PC_FILES"] = self.options.build_pc_files
        tc.variables["BUILD_TOOLS"] = self.options.build_tools
        tc.variables["BUILD_EXAMPLES"] = self.options.build_examples
        tc.variables["WITH_LIBZIP"] = self.options.with_libzip
        if Version(self.version) >= "0.2.34":
            tc.variables["WITH_MINIZIP_NG"] = self.options.with_minizip_ng
        tc.variables["WITH_WIDE"] = self.options.with_wide
        tc.variables["BUILD_DOCUMENTATION"] = self.options.build_documentation
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "xlsxio")
        self.cpp_info.set_property("cmake_module_file_name", "xlsxio")
        self.cpp_info.set_property("pkg_config_name", "xlsxio")

        if self.options.build_static :
            self.cpp_info.components["xlsxio_read_static"].set_property("cmake_target_name", "xlsxio::xlsxio_read_static")
            self.cpp_info.components["xlsxio_read_static"].set_property("cmake_module_target_name", "xlsxio::xlsxio_read_static")
            self.cpp_info.components["xlsxio_read_static"].set_property("pkg_config_name", "libxlsxio_read_static")
            self.cpp_info.components["xlsxio_write_static"].set_property("cmake_target_name", "xlsxio::xlsxio_write_static")
            self.cpp_info.components["xlsxio_write_static"].set_property("cmake_module_target_name", "xlsxio::xlsxio_write_static")
            self.cpp_info.components["xlsxio_write_static"].set_property("pkg_config_name", "libxlsxio_write_static")
            if self.options.with_wide:
                self.cpp_info.components["xlsxio_readw_static"].set_property("cmake_target_name", "xlsxio::xlsxio_readw_static")
                self.cpp_info.components["xlsxio_readw_static"].set_property("cmake_module_target_name", "xlsxio::xlsxio_readw_static")
                self.cpp_info.components["xlsxio_readw_static"].set_property("pkg_config_name", "libxlsxio_readw_static")
        if self.options.shared :
            self.cpp_info.components["xlsxio_read_shared"].set_property("cmake_target_name", "xlsxio::xlsxio_read_shared")
            self.cpp_info.components["xlsxio_read_shared"].set_property("cmake_module_target_name", "xlsxio::xlsxio_read_shared")
            self.cpp_info.components["xlsxio_read_shared"].set_property("pkg_config_name", "libxlsxio_read_shared")
            self.cpp_info.components["xlsxio_write_shared"].set_property("cmake_target_name", "xlsxio::xlsxio_write_shared")
            self.cpp_info.components["xlsxio_write_shared"].set_property("cmake_module_target_name", "xlsxio::xlsxio_write_shared")
            self.cpp_info.components["xlsxio_write_shared"].set_property("pkg_config_name", "libxlsxio_write_shared")
            if self.options.with_wide:
                self.cpp_info.components["xlsxio_readw_shared"].set_property("cmake_target_name", "xlsxio::xlsxio_readw_shared")
                self.cpp_info.components["xlsxio_readw_shared"].set_property("cmake_module_target_name", "xlsxio::xlsxio_readw_shared")
                self.cpp_info.components["xlsxio_readw_shared"].set_property("pkg_config_name", "libxlsxio_readw_shared")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "xlsxio"
        self.cpp_info.names["cmake_find_package_multi"] = "xlsxio"
        if self.options.build_static :
            self.cpp_info.components["xlsxio_read_static"].names["cmake_find_package"] = "xlsxio_read_static"
            self.cpp_info.components["xlsxio_read_static"].names["cmake_find_package_multi"] = "xlsxio_read_static"
            self.cpp_info.components["xlsxio_write_static"].names["cmake_find_package"] = "xlsxio_write_static"
            self.cpp_info.components["xlsxio_write_static"].names["cmake_find_package_multi"] = "xlsxio_write_static"
            if self.options.with_wide:
                self.cpp_info.components["xlsxio_readw_static"].names["cmake_find_package"] = "xlsxio_readw_static"
                self.cpp_info.components["xlsxio_readw_static"].names["cmake_find_package_multi"] = "xlsxio_readw_static"
        if self.options.shared :
            self.cpp_info.components["xlsxio_read_shared"].names["cmake_find_package"] = "xlsxio_read_shared"
            self.cpp_info.components["xlsxio_read_shared"].names["cmake_find_package_multi"] = "xlsxio_read_shared"
            self.cpp_info.components["xlsxio_write_shared"].names["cmake_find_package"] = "xlsxio_write_shared"
            self.cpp_info.components["xlsxio_write_shared"].names["cmake_find_package_multi"] = "xlsxio_write_shared"
            if self.options.with_wide:
                self.cpp_info.components["xlsxio_readw_shared"].names["cmake_find_package"] = "xlsxio_readw_shared"
                self.cpp_info.components["xlsxio_readw_shared"].names["cmake_find_package_multi"] = "xlsxio_readw_shared"
