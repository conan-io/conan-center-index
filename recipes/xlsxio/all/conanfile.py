from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
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
        "with_libzip": [True, False],
        "with_minizip_ng": [True, False],
        "with_wide": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "with_libzip": False,
        "with_minizip_ng": False,
        "with_wide": False,
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

        if self.options.with_wide:
            self.options["expat"].char_type = "ushort"
        if self.options.get_safe("with_minizip_ng"):
            self.options["minizip-ng"].mz_compatibility = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libzip:
            self.requires("libzip/1.10.1")
        elif Version(self.version) >= "0.2.34" and self.options.with_minizip_ng :
            self.requires("minizip-ng/4.0.1")
        else:
            self.requires("minizip/1.2.13")
        self.requires("expat/2.5.0")

    def validate(self):
        if Version(self.version) >= "0.2.34":
            if self.options.with_libzip and self.options.with_minizip_ng:
                raise ConanInvalidConfiguration("with_libzip and with_minizip_ng are mutually exclusive")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["WITH_LIBZIP"] = self.options.with_libzip
        if Version(self.version) >= "0.2.34":
            tc.variables["WITH_MINIZIP_NG"] = self.options.with_minizip_ng
        tc.variables["WITH_WIDE"] = self.options.with_wide
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
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
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xlsxio")

        ziplib = "minizip::minizip"
        if self.options.with_libzip:
            ziplib = "libzip::libzip"
        elif self.options.get_safe("with_minizip_ng"):
            ziplib = "minizip-ng::minizip-ng"

        xlsxio_macro = "BUILD_XLSXIO_SHARED" if self.options.shared else "BUILD_XLSXIO_STATIC"

        self.cpp_info.components["xlsxio_read"].set_property("cmake_target_name", "xlsxio::xlsxio_read")
        self.cpp_info.components["xlsxio_read"].set_property("pkg_config_name", "libxlsxio_read")
        self.cpp_info.components["xlsxio_read"].libs = ["xlsxio_read"]
        self.cpp_info.components["xlsxio_read"].requires = ["expat::expat", ziplib]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["xlsxio_read"].system_libs.append("pthread")
        self.cpp_info.components["xlsxio_read"].defines.append(xlsxio_macro)

        self.cpp_info.components["xlsxio_write"].set_property("cmake_target_name", "xlsxio::xlsxio_write")
        self.cpp_info.components["xlsxio_write"].set_property("pkg_config_name", "libxlsxio_write")
        self.cpp_info.components["xlsxio_write"].libs = ["xlsxio_write"]
        self.cpp_info.components["xlsxio_write"].requires = ["expat::expat", ziplib]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["xlsxio_write"].system_libs.append("pthread")
        self.cpp_info.components["xlsxio_write"].defines.append(xlsxio_macro)

        if self.options.with_wide:
            self.cpp_info.components["xlsxio_readw"].set_property("cmake_target_name", "xlsxio::xlsxio_readw")
            self.cpp_info.components["xlsxio_readw"].set_property("pkg_config_name", "libxlsxio_readw")
            self.cpp_info.components["xlsxio_readw"].libs = ["xlsxio_readw"]
            self.cpp_info.components["xlsxio_readw"].requires = ["expat::expat", ziplib]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["xlsxio_readw"].system_libs.append("pthread")
            self.cpp_info.components["xlsxio_readw"].defines.append(xlsxio_macro)

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "xlsxio"
        self.cpp_info.names["cmake_find_package_multi"] = "xlsxio"
        self.cpp_info.components["xlsxio_read"].names["cmake_find_package"] = "xlsxio_read"
        self.cpp_info.components["xlsxio_read"].names["cmake_find_package_multi"] = "xlsxio_read"
        self.cpp_info.components["xlsxio_write"].names["cmake_find_package"] = "xlsxio_write"
        self.cpp_info.components["xlsxio_write"].names["cmake_find_package_multi"] = "xlsxio_write"
        if self.options.with_wide:
            self.cpp_info.components["xlsxio_readw"].names["cmake_find_package"] = "xlsxio_readw"
            self.cpp_info.components["xlsxio_readw"].names["cmake_find_package_multi"] = "xlsxio_readw"

