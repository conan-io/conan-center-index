import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save, move_folder_contents
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class Hdf4Conan(ConanFile):
    name = "hdf4"
    description = "HDF4 is a data model, library, and file format for storing and managing data."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://portal.hdfgroup.org/display/HDF4/HDF4"
    topics = ("hdf", "data")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "jpegturbo": [True, False],
        "szip_support": [None, "with_libaec", "with_szip"],
        "szip_encoding": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "jpegturbo": False,
        "szip_support": None,
        "szip_encoding": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if not bool(self.options.szip_support):
            del self.options.szip_encoding

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.jpegturbo:
            self.requires("libjpeg-turbo/3.0.0")
        else:
            self.requires("libjpeg/9e")
        if self.options.szip_support == "with_libaec":
            self.requires("libaec/1.0.6")
        elif self.options.szip_support == "with_szip":
            self.requires("szip/2.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        if Version(self.version) > "4.2.15":
            move_folder_contents(self, os.path.join(self.source_folder, f"hdf-{self.version}"), self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["HDF4_EXTERNALLY_CONFIGURED"] = True
        tc.cache_variables["HDF4_EXTERNAL_LIB_PREFIX"] = ""
        tc.cache_variables["HDF4_NO_PACKAGES"] = True
        tc.cache_variables["ONLY_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["HDF4_ENABLE_COVERAGE"] = False
        tc.cache_variables["HDF4_ENABLE_DEPRECATED_SYMBOLS"] = True
        tc.cache_variables["HDF4_ENABLE_JPEG_LIB_SUPPORT"] = True  # HDF can't compile without libjpeg or libjpeg-turbo
        tc.cache_variables["HDF4_ENABLE_Z_LIB_SUPPORT"] = True  # HDF can't compile without zlib
        tc.cache_variables["HDF4_ENABLE_SZIP_SUPPORT"] = bool(self.options.szip_support)
        tc.cache_variables["HDF4_ENABLE_SZIP_ENCODING"] = self.options.get_safe("szip_encoding") or False
        tc.cache_variables["HDF4_PACKAGE_EXTLIBS"] = False
        tc.cache_variables["HDF4_BUILD_XDR_LIB"] = True
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["HDF4_INSTALL_INCLUDE_DIR"] = os.path.join(self.package_folder, "include", "hdf4").replace("\\", "/")
        tc.cache_variables["HDF4_BUILD_FORTRAN"] = False
        tc.cache_variables["HDF4_BUILD_UTILS"] = False
        tc.cache_variables["HDF4_BUILD_TOOLS"] = False
        tc.cache_variables["HDF4_BUILD_EXAMPLES"] = False
        tc.cache_variables["HDF4_BUILD_JAVA"] = False
        if cross_building(self):
            tc.cache_variables["H4_PRINTF_LL_TEST_RUN"] = "0"
            tc.cache_variables["H4_PRINTF_LL_TEST_RUN__TRYRUN_OUTPUT"] = ""
        tc.generate()

        deps = CMakeDeps(self)
        if self.options.szip_support == "with_szip":
            deps.set_property("szip", "cmake_file_name", "SZIP")
            deps.set_property("szip", "cmake_target_name", "SZIP::SZIP")
        elif self.options.szip_support == "with_libaec":
            deps.set_property("libaec", "cmake_file_name", "SZIP")
            deps.set_property("libaec", "cmake_target_name", "SZIP::SZIP")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        libs = ["JPEG::JPEG", "ZLIB::ZLIB"]
        if self.options.szip_support:
            libs.append("SZIP::SZIP")
        save(self, os.path.join(self.source_folder, "CMakeFilters.cmake"),
             "\nlink_libraries({})".format(" ".join(libs)), append=True)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libhdf4.settings"))

    def _get_decorated_lib(self, name):
        libname = name
        if self.settings.os == "Windows" and self.settings.compiler != "gcc" and not self.options.shared:
            libname = "lib" + libname
        if self.settings.build_type == "Debug":
            libname += "_D" if self.settings.os == "Windows" else "_debug"
        return libname

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "hdf")
        unofficial_includedir = os.path.join(self.package_folder, "include", "hdf4")
        target_suffix = "shared" if self.options.shared else "static"

        # xdr
        xdr_cmake = f"xdr-{target_suffix}"
        self.cpp_info.components["xdr"].set_property("cmake_target_name", f"hdf4::{xdr_cmake}")
        self.cpp_info.components["xdr"].names["cmake_find_package"] = xdr_cmake
        self.cpp_info.components["xdr"].names["cmake_find_package_multi"] = xdr_cmake
        self.cpp_info.components["xdr"].includedirs.append(unofficial_includedir)
        self.cpp_info.components["xdr"].libs = [self._get_decorated_lib("xdr")]
        if self.settings.os == "Windows":
            self.cpp_info.components["xdr"].system_libs.append("ws2_32")

        # hdf
        hdf_cmake = f"hdf-{target_suffix}"
        self.cpp_info.components["hdf"].set_property("cmake_target_name", f"hdf4::{hdf_cmake}")
        self.cpp_info.components["hdf"].names["cmake_find_package"] = hdf_cmake
        self.cpp_info.components["hdf"].names["cmake_find_package_multi"] = hdf_cmake
        self.cpp_info.components["hdf"].includedirs.append(unofficial_includedir)
        self.cpp_info.components["hdf"].libs = [self._get_decorated_lib("hdf")]
        self.cpp_info.components["hdf"].requires = [
            "zlib::zlib",
            "libjpeg-turbo::libjpeg-turbo" if self.options.jpegturbo else "libjpeg::libjpeg",
        ]
        if self.options.szip_support == "with_libaec":
            self.cpp_info.components["hdf"].requires.append("libaec::libaec")
        elif self.options.szip_support == "with_szip":
            self.cpp_info.components["hdf"].requires.append("szip::szip")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["hdf"].system_libs = ["m", "dl"]

        # mfhdf
        mfhdf_cmake = f"mfhdf-{target_suffix}"
        self.cpp_info.components["mfhdf"].set_property("cmake_target_name", f"hdf4::{mfhdf_cmake}")
        self.cpp_info.components["mfhdf"].names["cmake_find_package"] = mfhdf_cmake
        self.cpp_info.components["mfhdf"].names["cmake_find_package_multi"] = mfhdf_cmake
        self.cpp_info.components["mfhdf"].includedirs.append(unofficial_includedir)
        self.cpp_info.components["mfhdf"].libs = [self._get_decorated_lib("mfhdf")]
        self.cpp_info.components["mfhdf"].requires = ["xdr", "hdf"]

        if self.options.shared:
            self.cpp_info.components["xdr"].defines.append("H4_BUILT_AS_DYNAMIC_LIB=1")
            self.cpp_info.components["hdf"].defines.append("H4_BUILT_AS_DYNAMIC_LIB=1")
            self.cpp_info.components["mfhdf"].defines.append("H4_BUILT_AS_DYNAMIC_LIB=1")
