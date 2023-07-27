# TODO: verify the Conan v2 migration

import os

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.android import android_abi
from conan.tools.apple import XCRun, fix_apple_shared_install_name, is_apple_os, to_apple_arch
from conan.tools.build import build_jobs, can_run, check_min_cppstd, cross_building, default_cppstd, stdcpp_library, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import (
    apply_conandata_patches,
    chdir,
    collect_libs,
    copy,
    download,
    export_conandata_patches,
    get,
    load,
    mkdir,
    patch,
    patches,
    rename,
    replace_in_file,
    rm,
    rmdir,
    save,
    symlinks,
    unzip,
)
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfig, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import (
    MSBuild,
    MSBuildDeps,
    MSBuildToolchain,
    NMakeDeps,
    NMakeToolchain,
    VCVars,
    check_min_vs,
    is_msvc,
    is_msvc_static_runtime,
    msvc_runtime_flag,
    unix_path,
    unix_path_package_info_legacy,
    vs_layout,
)
from conan.tools.scm import Version
from conan.tools.system import package_manager
import functools
import os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

required_conan_version = ">=1.52.0"


class GdalConan(ConanFile):
    name = "gdal"
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OSGeo/gdal"
    topics = ("osgeo", "geospatial", "raster", "vector", "pre-built")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    # A list of gdal dependencies can be taken from cmake/helpers/CheckDependentLibraries.cmake
    # within gdal sources with the command:
    # grep -E '^[ \t]*gdal_check_package\(' cmake/helpers/CheckDependentLibraries.cmake \
    #   | sed 's/[ \t]*gdal_check_package(\([a-zA-Z_0-9]\+\) "\(.*\)"\(.*\)/{ 'dep': \'\1\', 'descr': \'\2\' },/' \
    #   | sort | uniq

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "with_armadillo": [True, False],
        "with_arrow": [True, False],
        "with_blosc": [True, False],
        "with_cfitsio": [True, False],
        # with_cypto option has been renamed with_openssl in version 3.5.1
        "with_crypto": [True, False, "deprecated"],
        "with_cryptopp": [True, False],
        "with_curl": [True, False],
        "with_dds": [True, False],
        "with_expat": [True, False],
        "with_exr": [True, False],
        "with_freexl": [True, False],
        "with_geos": [True, False],
        "with_gif": [True, False],
        "with_gta": [True, False],
        "with_hdf4": [True, False],
        "with_hdf5": [True, False],
        "with_heif": [True, False],
        "with_kea": [True, False],
        "with_libdeflate": [True, False],
        "with_libiconv": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_libkml": [True, False],
        "with_libtiff": [True, False],
        "with_lz4": [True, False],
        "with_mongocxx": [True, False],
        "with_mysql": [None, "libmysqlclient", "mariadb-connector-c"],
        "with_netcdf": [True, False],
        "with_odbc": [True, False],
        "with_openjpeg": [True, False],
        "with_openssl": [True, False],
        "with_pcre": [True, False],
        "with_pcre2": [True, False],
        "with_pg": [True, False],
        "with_png": [True, False],
        "with_podofo": [True, False],
        "with_poppler": [True, False],
        "with_proj": [True, False],
        "with_qhull": [True, False],
        "with_sqlite3": [True, False],
        "with_webp": [True, False],
        "with_xerces": [True, False],
        "with_xml2": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": False,
        "with_armadillo": False,
        "with_arrow": False,
        "with_blosc": False,
        "with_cfitsio": False,
        "with_crypto": "deprecated",
        "with_cryptopp": False,
        "with_curl": False,
        "with_dds": False,
        "with_expat": False,
        "with_exr": False,
        "with_freexl": False,
        "with_geos": True,
        "with_gif": True,
        "with_gta": False,
        "with_hdf4": False,
        "with_hdf5": False,
        "with_heif": False,
        "with_kea": False,
        "with_libdeflate": True,
        "with_libiconv": True,
        "with_jpeg": "libjpeg",
        "with_libkml": False,
        "with_libtiff": True,
        "with_lz4": False,
        "with_mongocxx": False,
        "with_mysql": None,
        "with_netcdf": False,
        "with_odbc": False,
        "with_openjpeg": False,
        "with_openssl": False,
        "with_pcre": False,
        "with_pcre2": False,
        "with_pg": False,
        "with_png": True,
        "with_podofo": False,
        "with_poppler": False,
        "with_proj": True,
        "with_qhull": True,
        "with_sqlite3": True,
        "with_webp": False,
        "with_xerces": False,
        "with_xml2": False,
        "with_zlib": True,
        "with_zstd": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.with_crypto != "deprecated":
            self.output.error("with_crypto option is deprecated, use with_openssl instead.")

        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.options["hdf4"].jpegturbo = self.options.with_jpeg == "libjpeg-turbo"
        self.options["libtiff"].jpeg = self.options.with_jpeg
        # TODO: add libjpeg options to poppler and podofo recipes
        # self.options["poppler"].with_libjpeg = self.options.with_jpeg
        # self.options["podofo"].with_libjpeg = self.options.with_jpeg

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("json-c/0.16")
        self.requires("libgeotiff/1.7.1")

        if self.options.with_armadillo:
            self.requires("armadillo/12.2.0")

        if self.options.with_arrow:
            self.requires("arrow/12.0.0")

        if self.options.with_blosc:
            self.requires("c-blosc/1.21.4")

        if self.options.with_cfitsio:
            self.requires("cfitsio/4.2.0")

        if self.options.with_cryptopp:
            self.requires("cryptopp/8.7.0")

        if self.options.with_curl:
            self.requires("libcurl/8.2.1")

        if self.options.with_dds:
            self.requires("crunch/cci.20190615")

        if self.options.with_expat:
            self.requires("expat/2.5.0")

        if self.options.with_exr:
            self.requires("openexr/3.1.9")
            self.requires("imath/3.1.9")

        if self.options.with_freexl:
            self.requires("freexl/1.0.6")

        if self.options.with_geos:
            self.requires("geos/3.11.2")

        if self.options.with_gif:
            self.requires("giflib/5.2.1")

        if self.options.with_gta:
            self.requires("libgta/1.2.1")

        if self.options.with_hdf4:
            self.requires("hdf4/4.2.15")

        if self.options.with_hdf5:
            self.requires("hdf5/1.14.1")

        if self.options.with_heif:
            self.requires("libheif/1.13.0")

        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")

        if self.options.with_kea:
            self.requires("kealib/1.4.14")

        if self.options.with_libdeflate:
            self.requires("libdeflate/1.18")

        if self.options.with_libiconv:
            self.requires("libiconv/1.17")

        if self.options.with_libkml:
            self.requires("libkml/1.3.0")

        if self.options.with_libtiff:
            self.requires("libtiff/4.5.1")

        if self.options.with_lz4:
            self.requires("lz4/1.9.4")

        if self.options.with_mongocxx:
            self.requires("mongo-cxx-driver/3.7.2")

        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.1.0")
        elif self.options.with_mysql == "mariadb-connector-c":
            self.requires("mariadb-connector-c/3.3.3")

        if self.options.with_netcdf:
            self.requires("netcdf/4.8.1")

        if self.options.with_odbc:
            self.requires("odbc/2.3.11")

        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1v")

        if self.options.with_pcre:
            self.requires("pcre/8.45")

        if self.options.with_pcre2:
            self.requires("pcre2/10.42")

        if self.options.with_pg:
            self.requires("libpq/15.3")

        if self.options.with_png:
            self.requires("libpng/1.6.40")

        if self.options.with_podofo:
            self.requires("podofo/0.9.7")

        if self.options.with_poppler:
            self.requires("poppler/21.07.0")

        if self.options.with_proj:
            self.requires("proj/9.2.1")

        if self.options.with_qhull:
            self.requires("qhull/8.0.1")

        if self.options.with_sqlite3:
            self.requires("sqlite3/3.42.0")

        if self.options.with_webp:
            self.requires("libwebp/1.3.1")

        if self.options.with_xerces:
            self.requires("xerces-c/3.2.4")

        if self.options.with_xml2:
            self.requires("libxml2/2.11.4")

        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

    def build_requirements(self):
        # https://github.com/conan-io/conan/issues/3482#issuecomment-662284561
        self.tool_requires("cmake/[>=3.18 <4]")

    def package_id(self):
        del self.info.options.with_crypto

    def validate(self):
        if self.options.get_safe("with_pcre") and self.options.get_safe("with_pcre2"):
            raise ConanInvalidConfiguration("Enable either pcre or pcre2, not both")

        if self.options.get_safe("with_sqlite3") and not self.dependencies["sqlite3"].options.enable_column_metadata:
            raise ConanInvalidConfiguration("gdql requires sqlite3:enable_column_metadata=True")

        if self.options.get_safe("with_libtiff") and self.dependencies["libtiff"].options.jpeg != self.options.get_safe("with_jpeg"):
            msg = "libtiff:jpeg and gdal:with_jpeg must be set to the same value, either libjpeg or libjpeg-turbo."
            # For some reason, the ConanInvalidConfiguration message is not shown, only
            #     ERROR: At least two recipes provides the same functionality:
            #      - 'libjpeg' provided by 'libjpeg-turbo/2.1.2', 'libjpeg/9d'
            # So we print the error message manually.
            self.output.error(msg)
            raise ConanInvalidConfiguration(msg)

        if self.options.get_safe("with_poppler") and self.dependencies["poppler"].options.with_libjpeg != self.options.get_safe("with_jpeg"):
            msg = "poppler:with_libjpeg and gdal:with_jpeg must be set to the same value, either libjpeg or" " libjpeg-turbo."
            self.output.error(msg)
            raise ConanInvalidConfiguration(msg)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        if self.options.get_safe("fPIC", True):
            tc.variables["GDAL_OBJECT_LIBRARIES_POSITION_INDEPENDENT_CODE"] = True

        tc.variables["BUILD_JAVA_BINDINGS"] = False
        tc.variables["BUILD_CSHARP_BINDINGS"] = False
        tc.variables["BUILD_PYTHON_BINDINGS"] = False

        tc.variables["BUILD_TESTING"] = False
        tc.variables["GDAL_USE_ZLIB_INTERNAL"] = False
        tc.variables["GDAL_USE_JSONC_INTERNAL"] = False
        tc.variables["GDAL_USE_JPEG_INTERNAL"] = False
        tc.variables["GDAL_USE_JPEG12_INTERNAL"] = False
        tc.variables["GDAL_USE_TIFF_INTERNAL"] = False
        tc.variables["GDAL_USE_GEOTIFF_INTERNAL"] = False
        tc.variables["GDAL_USE_GIF_INTERNAL"] = False
        tc.variables["GDAL_USE_PNG_INTERNAL"] = False

        tc.variables["GDAL_USE_LERC_INTERNAL"] = True
        tc.variables["GDAL_USE_SHAPELIB_INTERNAL"] = True

        tc.variables["BUILD_APPS"] = self.options.tools

        tc.variables["SQLite3_HAS_COLUMN_METADATA"] = self.dependencies["sqlite3"].options.enable_column_metadata

        tc.variables["SQLite3_HAS_RTREE"] = self.dependencies["sqlite3"].options.enable_rtree

        tc.variables["GDAL_USE_JSONC"] = True
        tc.variables["GDAL_CONAN_PACKAGE_FOR_JSONC"] = "json-c"

        tc.variables["GDAL_USE_GEOTIFF"] = True
        tc.variables["GDAL_CONAN_PACKAGE_FOR_GEOTIFF"] = "libgeotiff"
        tc.variables["TARGET_FOR_GEOTIFF"] = "GeoTIFF::GeoTIFF"

        tc.variables["GDAL_USE_ARMADILLO"] = self.options.with_armadillo
        if self.options.with_armadillo:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_ARMADILLO"] = "armadillo"
            tc.variables["TARGET_FOR_ARMADILLO"] = self.dependencies["armadillo"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Armadillo_FOUND"] = False

        tc.variables["GDAL_USE_ARROW"] = self.options.with_arrow
        if self.options.with_arrow:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_ARROW"] = "arrow"
            tc.variables["TARGET_FOR_ARROW"] = self.dependencies["arrow"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Arrow_FOUND"] = False

        tc.variables["GDAL_USE_BLOSC"] = self.options.with_blosc
        if self.options.with_blosc:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_BLOSC"] = "c-blosc"
            tc.variables["TARGET_FOR_BLOSC"] = self.dependencies["c-blosc"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Blosc_FOUND"] = False

        tc.variables["GDAL_USE_CFITSIO"] = self.options.with_cfitsio
        if self.options.with_cfitsio:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_CFITSIO"] = "cfitsio"
            tc.variables["TARGET_FOR_CFITSIO"] = self.dependencies["cfitsio"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["CFITSIO_FOUND"] = False

        tc.variables["GDAL_USE_CRYPTOPP"] = self.options.with_cryptopp
        if self.options.with_cryptopp:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_CRYPTOPP"] = "cryptopp"
            tc.variables["TARGET_FOR_CRYPTOPP"] = self.dependencies["cryptopp"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["CryptoPP_FOUND"] = False

        tc.variables["GDAL_USE_CURL"] = self.options.with_curl
        if self.options.with_curl:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_CURL"] = "libcurl"
            tc.variables["TARGET_FOR_CURL"] = self.dependencies["libcurl"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["CURL_FOUND"] = False

        tc.variables["GDAL_USE_CRNLIB"] = self.options.with_dds
        if self.options.with_dds:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_CRNLIB"] = "crunch"
            tc.variables["TARGET_FOR_CRNLIB"] = self.dependencies["crunch"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Crnlib_FOUND"] = False

        tc.variables["GDAL_USE_EXPAT"] = self.options.with_expat
        if self.options.with_expat:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_EXPAT"] = "expat"
            tc.variables["TARGET_FOR_EXPAT"] = "EXPAT::EXPAT"
        else:
            tc.variables["EXPAT_FOUND"] = False

        tc.variables["GDAL_USE_OPENEXR"] = self.options.with_exr
        if self.options.with_exr:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_OPENEXR"] = "openexr"
            tc.variables["TARGET_FOR_OPENEXR"] = self.dependencies["openexr"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["OpenEXR_FOUND"] = False

        tc.variables["GDAL_USE_FREEXL"] = self.options.with_freexl
        if self.options.with_freexl:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_FREEXL"] = "freexl"
            tc.variables["TARGET_FOR_FREEXL"] = "freexl::freexl"
        else:
            tc.variables["FreeXL_FOUND"] = False

        tc.variables["GDAL_USE_GEOS"] = self.options.with_geos
        if self.options.with_geos:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_GEOS"] = "geos"
            tc.variables["TARGET_FOR_GEOS"] = self.dependencies["geos"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["GEOS_FOUND"] = False

        tc.variables["GDAL_USE_GIF"] = self.options.with_gif
        if self.options.with_gif:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_GIF"] = "giflib"
            tc.variables["TARGET_FOR_GIF"] = self.dependencies["giflib"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["GIF_FOUND"] = False

        tc.variables["GDAL_USE_GTA"] = self.options.with_gta
        if self.options.with_gta:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_GTA"] = "libgta"
            tc.variables["TARGET_FOR_GTA"] = self.dependencies["libgta"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["GTA_FOUND"] = False

        tc.variables["GDAL_USE_HDF4"] = self.options.with_hdf4
        if self.options.with_hdf4:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_HDF4"] = "hdf4"
            tc.variables["TARGET_FOR_HDF4"] = self.dependencies["hdf4"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["HDF4_FOUND"] = False

        tc.variables["GDAL_USE_HDF5"] = self.options.with_hdf5
        if self.options.with_hdf5:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_HDF5"] = "hdf5"
            tc.variables["TARGET_FOR_HDF5"] = self.dependencies["hdf5"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["HDF5_FOUND"] = False

        tc.variables["GDAL_USE_HEIF"] = self.options.with_heif
        if self.options.with_heif:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_HEIF"] = "libheif"
            tc.variables["TARGET_FOR_HEIF"] = self.dependencies["libheif"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["HEIF_FOUND"] = False

        tc.variables["GDAL_USE_KEA"] = self.options.with_kea
        if self.options.with_kea:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_KEA"] = "kealib"
            tc.variables["TARGET_FOR_KEA"] = self.dependencies["kealib"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["KEA_FOUND"] = False

        tc.variables["GDAL_USE_DEFLATE"] = self.options.with_libdeflate
        if self.options.with_libdeflate:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_DEFLATE"] = "libdeflate"
            tc.variables["TARGET_FOR_DEFLATE"] = self.dependencies["libdeflate"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Deflate_FOUND"] = False

        tc.variables["GDAL_USE_ICONV"] = self.options.with_libiconv
        if self.options.with_libiconv:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_ICONV"] = "libiconv"
            tc.variables["TARGET_FOR_ICONV"] = self.dependencies["libiconv"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Iconv_FOUND"] = False

        if self.options.with_jpeg == "libjpeg" or self.options.with_jpeg == "libjpeg-turbo":
            print(f"self.options.with_jpeg: {self.options.with_jpeg}")
            tc.variables["GDAL_USE_JPEG"] = True
            tc.variables["GDAL_CONAN_PACKAGE_FOR_JPEG"] = self.options.with_jpeg
            tc.variables["TARGET_FOR_JPEG"] = (
                "JPEG::JPEG"
                if self.options.with_jpeg == "libjpeg"
                else self.dependencies["libjpeg-turbo"].cpp_info.components["turbojpeg"].get_property("cmake_target_name")
            )
        else:
            tc.variables["JPEG_FOUND"] = False

        tc.variables["GDAL_USE_LIBKML"] = self.options.with_libkml
        if self.options.with_libkml:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_LIBKML"] = "libkml"
            tc.variables["TARGET_FOR_LIBKML"] = self.dependencies["libkml"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["LibKML_FOUND"] = False

        tc.variables["GDAL_USE_TIFF"] = self.options.with_libtiff
        if self.options.with_libtiff:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_TIFF"] = "libtiff"
            tc.variables["TARGET_FOR_TIFF"] = self.dependencies["libtiff"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["TIFF_FOUND"] = False

        tc.variables["GDAL_USE_LZ4"] = self.options.with_lz4
        if self.options.with_lz4:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_LZ4"] = "lz4"
            tc.variables["TARGET_FOR_LZ4"] = self.dependencies["lz4"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["LZ4_FOUND"] = False

        tc.variables["GDAL_USE_MONGOCXX"] = self.options.with_mongocxx
        if self.options.with_mongocxx:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_MONGOCXX"] = "mongo-cxx-driver"
            tc.variables["TARGET_FOR_MONGOCXX"] = self.dependencies["mongo-cxx-driver"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["MONGOCXX_FOUND"] = False

        if self.options.with_mysql == "libmysqlclient" or self.options.with_mysql == "mariadb-connector-c":
            tc.variables["GDAL_CONAN_PACKAGE_FOR_MYSQL"] = str(self.options.with_mysql)
            tc.variables["TARGET_FOR_MYSQL"] = (
                "mariadb-connector-c::mariadb-connector-c"
                if self.options.with_mysql == "mariadb-connector-c"
                else "libmysqlclient::libmysqlclient"
            )
        else:
            tc.variables["MYSQL_FOUND"] = False

        tc.variables["GDAL_USE_NETCDF"] = self.options.with_netcdf
        if self.options.with_netcdf:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_NETCDF"] = "netcdf"
            tc.variables["TARGET_FOR_NETCDF"] = self.dependencies["netcdf"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["NetCDF_FOUND"] = False

        tc.variables["GDAL_USE_ODBC"] = self.options.with_odbc
        if self.options.with_odbc:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_ODBC"] = "odbc"
            tc.variables["TARGET_FOR_ODBC"] = self.dependencies["odbc"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["ODBC_FOUND"] = False

        tc.variables["GDAL_USE_OPENJPEG"] = self.options.with_openjpeg
        if self.options.with_openjpeg:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_OPENJPEG"] = "openjpeg"
            tc.variables["TARGET_FOR_OPENJPEG"] = self.dependencies["openjpeg"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["OPENJPEG_FOUND"] = False

        tc.variables["GDAL_USE_OPENSSL"] = self.options.with_openssl
        if self.options.with_openssl:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_OPENSSL"] = "openssl"
            tc.variables["TARGET_FOR_OPENSSL"] = self.dependencies["openssl"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["OpenSSL_FOUND"] = False

        tc.variables["GDAL_USE_PCRE"] = self.options.with_pcre
        if self.options.with_pcre:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_PCRE"] = "pcre"
            tc.variables["TARGET_FOR_PCRE"] = self.dependencies["pcre"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["PCRE_FOUND"] = False

        tc.variables["GDAL_USE_PCRE2"] = self.options.with_pcre2
        if self.options.with_pcre2:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_PCRE2"] = "pcre2"
            tc.variables["TARGET_FOR_PCRE2"] = self.dependencies["pcre2"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["PCRE2_FOUND"] = False

        tc.variables["GDAL_USE_PDFIUM"] = False
        tc.variables["PDFIUM_FOUND"] = False

        tc.variables["GDAL_USE_POSTGRESQL"] = self.options.with_pg
        if self.options.with_pg:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_POSTGRESQL"] = "libpq"
            tc.variables["TARGET_FOR_POSTGRESQL"] = self.dependencies["libpq"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["PostgreSQL_FOUND"] = False

        tc.variables["GDAL_USE_PNG"] = self.options.with_png
        if self.options.with_png:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_PNG"] = "libpng"
            tc.variables["TARGET_FOR_PNG"] = self.dependencies["libpng"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["PNG_FOUND"] = False

        tc.variables["GDAL_USE_PODOFO"] = self.options.with_podofo
        if self.options.with_podofo:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_PODOFO"] = "podofo"
            tc.variables["TARGET_FOR_PODOFO"] = self.dependencies["podofo"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Podofo_FOUND"] = False

        tc.variables["GDAL_USE_POPPLER"] = self.options.with_poppler
        if self.options.with_poppler:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_POPPLER"] = "poppler"
            tc.variables["TARGET_FOR_POPPLER"] = self.dependencies["poppler"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["Poppler_FOUND"] = False

        tc.variables["GDAL_USE_PROJ"] = self.options.with_proj
        if self.options.with_proj:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_PROJ"] = "proj"
            tc.variables["TARGET_FOR_PROJ"] = self.dependencies["proj"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["PROJ_FOUND"] = False

        tc.variables["GDAL_USE_QHULL"] = self.options.with_qhull
        if self.options.with_qhull:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_QHULL"] = "qhull"
            tc.variables["TARGET_FOR_QHULL"] = self.dependencies["qhull"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["QHULL_FOUND"] = False

        tc.variables["GDAL_USE_SQLITE3"] = self.options.with_sqlite3
        if self.options.with_sqlite3:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_SQLITE3"] = "sqlite3"
            tc.variables["TARGET_FOR_SQLITE3"] = self.dependencies["sqlite3"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["SQLite3_FOUND"] = False

        tc.variables["GDAL_USE_WEBP"] = self.options.with_webp
        if self.options.with_webp:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_WEBP"] = "libwebp"
            tc.variables["TARGET_FOR_WEBP"] = self.dependencies["libwebp"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["WebP_FOUND"] = False

        tc.variables["GDAL_USE_XERCESC"] = self.options.with_xerces
        if self.options.with_xerces:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_XERCESC"] = "xerces-c"
            tc.variables["TARGET_FOR_XERCESC"] = self.dependencies["xerces-c"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["XercesC_FOUND"] = False

        tc.variables["GDAL_USE_LIBXML2"] = self.options.with_xml2
        if self.options.with_xml2:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_LIBXML2"] = "libxml2"
            tc.variables["TARGET_FOR_LIBXML2"] = self.dependencies["libxml2"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["LibXml2_FOUND"] = False

        tc.variables["GDAL_USE_ZLIB"] = self.options.with_zlib
        if self.options.with_zlib:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_ZLIB"] = "zlib"
            tc.variables["TARGET_FOR_ZLIB"] = self.dependencies["zlib"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["ZLIB_FOUND"] = False

        tc.variables["GDAL_USE_ZSTD"] = self.options.with_zstd
        if self.options.with_zstd:
            tc.variables["GDAL_CONAN_PACKAGE_FOR_ZSTD"] = "zstd"
            tc.variables["TARGET_FOR_ZSTD"] = self.dependencies["zstd"].cpp_info.get_property("cmake_target_name")
        else:
            tc.variables["ZSTD_FOUND"] = False

        for k, v in tc.variables.items():
            print(k, " = ", v)

        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE.TXT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GDAL")
        self.cpp_info.set_property("cmake_target_name", "GDAL::GDAL")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "gdal")

        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "GDAL"

        libname = "gdal"
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                libname += "d"
        self.cpp_info.libs = [libname]

        self.cpp_info.requires.extend(['json-c::json-c'])
        self.cpp_info.requires.extend(['libgeotiff::libgeotiff'])

        if self.options.with_armadillo:
            self.cpp_info.requires.extend(['armadillo::armadillo'])

        if self.options.with_arrow:
            self.cpp_info.requires.extend(['arrow::libarrow'])

        if self.options.with_blosc:
            self.cpp_info.requires.extend(['c-blosc::c-blosc'])

        if self.options.with_cfitsio:
            self.cpp_info.requires.extend(['cfitsio::cfitsio'])

        if self.options.with_cryptopp:
            self.cpp_info.requires.extend(['cryptopp::libcryptopp'])

        if self.options.with_curl:
            self.cpp_info.requires.extend(['libcurl::curl'])

        if self.options.with_dds:
            self.cpp_info.requires.extend(['crunch::crunch'])

        if self.options.with_expat:
            self.cpp_info.requires.extend(['expat::expat'])

        if self.options.with_exr:
            self.cpp_info.requires.extend(['openexr::openexr', 'imath::imath'])

        if self.options.with_freexl:
            self.cpp_info.requires.extend(['freexl::freexl'])

        if self.options.with_geos:
            self.cpp_info.requires.extend(['geos::geos_c'])

        if self.options.with_gif:
            self.cpp_info.requires.extend(['giflib::giflib'])

        if self.options.with_gta:
            self.cpp_info.requires.extend(['libgta::libgta'])

        if self.options.with_hdf4:
            self.cpp_info.requires.extend(['hdf4::hdf4'])

        if self.options.with_hdf5:
            self.cpp_info.requires.extend(['hdf5::hdf5_c'])

        if self.options.with_heif:
            self.cpp_info.requires.extend(['libheif::libheif'])

        if self.options.with_kea:
            self.cpp_info.requires.extend(['kealib::kealib'])

        if self.options.with_libdeflate:
            self.cpp_info.requires.extend(['libdeflate::libdeflate'])

        if self.options.with_libiconv:
            self.cpp_info.requires.extend(['libiconv::libiconv'])

        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.requires.extend(['libjpeg::libjpeg'])
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.requires.extend(['libjpeg-turbo::turbojpeg'])

        if self.options.with_libkml:
            self.cpp_info.requires.extend(['libkml::kmldom', 'libkml::kmlengine'])

        if self.options.with_libtiff:
            self.cpp_info.requires.extend(['libtiff::libtiff'])

        if self.options.with_lz4:
            self.cpp_info.requires.extend(['lz4::lz4'])

        if self.options.with_mongocxx:
            self.cpp_info.requires.extend(['mongo-cxx-driver::mongo-cxx-driver'])

        if self.options.with_mysql == "libmysqlclient":
            self.cpp_info.requires.extend(['libmysqlclient::libmysqlclient'])
        elif self.options.with_mysql == "mariadb-connector-c":
            self.cpp_info.requires.extend(['mariadb-connector-c::mariadb-connector-c'])

        if self.options.with_netcdf:
            self.cpp_info.requires.extend(['netcdf::netcdf'])

        if self.options.with_odbc:
            self.cpp_info.requires.extend(['odbc::odbc'])

        if self.options.with_openjpeg:
            self.cpp_info.requires.extend(['openjpeg::openjpeg'])

        if self.options.with_openssl:
            self.cpp_info.requires.extend(['openssl::ssl'])

        if self.options.with_pcre:
            self.cpp_info.requires.extend(['pcre::pcre'])

        if self.options.with_pcre2:
            self.cpp_info.requires.extend(['pcre2::pcre2-8'])

        if self.options.with_pg:
            self.cpp_info.requires.extend(['libpq::pq'])

        if self.options.with_png:
            self.cpp_info.requires.extend(['libpng::libpng'])

        if self.options.with_podofo:
            self.cpp_info.requires.extend(['podofo::podofo'])

        if self.options.with_poppler:
            self.cpp_info.requires.extend(['poppler::libpoppler'])

        if self.options.with_proj:
            self.cpp_info.requires.extend(['proj::projlib'])

        if self.options.with_qhull:
            self.cpp_info.requires.extend(['qhull::libqhull'])

        if self.options.with_sqlite3:
            self.cpp_info.requires.extend(['sqlite3::sqlite'])

        if self.options.with_webp:
            self.cpp_info.requires.extend(['libwebp::libwebp'])

        if self.options.with_xerces:
            self.cpp_info.requires.extend(['xerces-c::xerces-c'])

        if self.options.with_xml2:
            self.cpp_info.requires.extend(['libxml2::libxml2'])

        if self.options.with_zlib:
            self.cpp_info.requires.extend(['zlib::zlib'])

        if self.options.with_zstd:
            self.cpp_info.requires.extend(['zstd::zstdlib'])

        gdal_data_path = os.path.join(self.package_folder, "res", "gdal")
        self.output.info(f"Prepending to GDAL_DATA environment variable: {gdal_data_path}")
        self.runenv_info.prepend_path("GDAL_DATA", gdal_data_path)
        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.GDAL_DATA = gdal_data_path

        if self.options.tools:
            self.buildenv_info.prepend_path("GDAL_DATA", gdal_data_path)
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
