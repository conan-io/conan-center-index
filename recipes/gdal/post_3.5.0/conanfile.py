from conan import ConanFile
from conan.tools.files import apply_conandata_patches, get, files
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
from conans import CMake
import functools
import os
import re

class GdalConan(ConanFile):
    name = "gdal"
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    topics = ("osgeo", "geospatial", "raster", "vector")
    homepage = "https://github.com/OSGeo/gdal"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake", "cmake_find_package"

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
        "with_crypto": [True, False],
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
        "with_crypto": False, # deprecated, replaced by with_openssl
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("json-c/0.15")
        self.requires("libgeotiff/1.7.1")

        if self.options.with_armadillo:
            self.requires("armadillo/10.7.3")

        if self.options.with_arrow:
            self.requires("arrow/8.0.0")

        if self.options.with_blosc:
            self.requires("c-blosc/1.21.1")

        if self.options.with_cfitsio:
            self.requires("cfitsio/4.1.0")

        if self.options.with_cryptopp:
            self.requires("cryptopp/8.6.0")

        if self.options.with_curl:
            self.requires("libcurl/7.83.1")

        if self.options.with_dds:
            self.requires("crunch/cci.20190615")

        if self.options.with_expat:
            self.requires("expat/2.4.8")

        if self.options.with_exr:
            self.requires("openexr/3.1.5")
            self.requires("imath/3.1.5")

        if self.options.with_freexl:
            self.requires("freexl/1.0.6")

        if self.options.with_geos:
            self.requires("geos/3.11.0")

        if self.options.with_gif:
            self.requires("giflib/5.2.1")

        if self.options.with_gta:
            self.requires("libgta/1.2.1")

        if self.options.with_hdf4:
            self.requires("hdf4/4.2.15")

        if self.options.with_hdf5:
            self.requires("hdf5/1.13.1")

        if self.options.with_heif:
            self.requires("libheif/1.12.0")

        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")

        if self.options.with_kea:
            self.requires("kealib/1.4.14")

        if self.options.with_libdeflate:
            self.requires("libdeflate/1.12")

        if self.options.with_libiconv:
            self.requires("libiconv/1.17")

        if self.options.with_libkml:
            self.requires("libkml/1.3.0")

        if self.options.with_libtiff:
            self.requires("libtiff/4.3.0")

        if self.options.with_lz4:
            self.requires("lz4/1.9.3")

        if self.options.with_mongocxx:
            self.requires("mongo-cxx-driver/3.6.6")

        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.0.29")
        elif self.options.with_mysql == "mariadb-connector-c":
            self.requires("mariadb-connector-c/3.1.12")

        if self.options.with_netcdf:
            self.requires("netcdf/4.8.1")

        if self.options.with_odbc:
            self.requires("odbc/2.3.9")

        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1o")

        if self.options.with_pcre:
            self.requires("pcre/8.45")

        if self.options.with_pcre2:
            self.requires("pcre2/10.40")

        if self.options.with_pg:
            self.requires("libpq/14.2")

        if self.options.with_png:
            self.requires("libpng/1.6.37")

        if self.options.with_podofo:
            self.requires("podofo/0.9.7")

        if self.options.with_poppler:
            self.requires("poppler/21.07.0")

        if self.options.with_proj:
            self.requires("proj/9.0.0")

        if self.options.with_qhull:
            self.requires("qhull/8.0.1")

        if self.options.with_sqlite3:
            self.requires("sqlite3/3.38.5")

        if self.options.with_webp:
            self.requires("libwebp/1.2.2")

        if self.options.with_xerces:
            self.requires("xerces-c/3.2.3")

        if self.options.with_xml2:
            self.requires("libxml2/2.9.14")

        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

        if self.options.with_zstd:
            self.requires("zstd/1.5.2")

    def validate(self):
        if self.options.get_safe("with_crypto"):
            raise ConanInvalidConfiguration("with_crypto option has been replaced by with_openssl")

        if self.options.get_safe("with_pcre") and self.options.get_safe("with_pcre2"):
            raise ConanInvalidConfiguration("Enable either pcre or pcre2, not both")

        if self.options.get_safe("with_sqlite3") and not self.options["sqlite3"].enable_column_metadata:
            raise ConanInvalidConfiguration("gdql requires sqlite3:enable_column_metadata=True")

        if self.options.get_safe("with_libtiff") and self.options["libtiff"].jpeg != self.options.get_safe("with_jpeg"):
            msg = "libtiff:jpeg and gdal:with_jpeg must be set to the same value, either libjpeg or libjpeg-turbo."
            # For some reason, the ConanInvalidConfiguration message is not shown, only
            #     ERROR: At least two recipes provides the same functionality:
            #      - 'libjpeg' provided by 'libjpeg-turbo/2.1.2', 'libjpeg/9d'
            # So we print the error message manually.
            self.output.error(msg)
            raise ConanInvalidConfiguration(msg)

        if self.options.get_safe("with_poppler") and self.options["poppler"].with_libjpeg != self.options.get_safe("with_jpeg"):
            msg = "poppler:with_libjpeg and gdal:with_jpeg must be set to the same value, either libjpeg or libjpeg-turbo."
            self.output.error(msg)
            raise ConanInvalidConfiguration(msg)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.get_safe("fPIC", True):
            cmake.definitions[
                "GDAL_OBJECT_LIBRARIES_POSITION_INDEPENDENT_CODE"] = True

        cmake.definitions["BUILD_JAVA_BINDINGS"] = False
        cmake.definitions["BUILD_CSHARP_BINDINGS"] = False
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = False

        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["GDAL_USE_ZLIB_INTERNAL"] = False
        cmake.definitions["GDAL_USE_JSONC_INTERNAL"] = False
        cmake.definitions["GDAL_USE_JPEG_INTERNAL"] = False
        cmake.definitions["GDAL_USE_JPEG12_INTERNAL"] = False
        cmake.definitions["GDAL_USE_TIFF_INTERNAL"] = False
        cmake.definitions["GDAL_USE_GEOTIFF_INTERNAL"] = False
        cmake.definitions["GDAL_USE_GIF_INTERNAL"] = False
        cmake.definitions["GDAL_USE_PNG_INTERNAL"] = False

        cmake.definitions["GDAL_USE_LERC_INTERNAL"] = True
        cmake.definitions["GDAL_USE_SHAPELIB_INTERNAL"] = True

        cmake.definitions["BUILD_APPS"] = self.options.tools

        cmake.definitions["SQLite3_HAS_COLUMN_METADATA"] = \
            self.options["sqlite3"].enable_column_metadata

        cmake.definitions["SQLite3_HAS_RTREE"] = self.options[
            "sqlite3"].enable_rtree

        cmake.definitions["GDAL_USE_JSONC"] = True
        cmake.definitions["GDAL_CONAN_PACKAGE_FOR_JSONC"] = "json-c"

        cmake.definitions["GDAL_USE_GEOTIFF"] = True
        cmake.definitions["GDAL_CONAN_PACKAGE_FOR_GEOTIFF"] = "libgeotiff"
        cmake.definitions["TARGET_FOR_GEOTIFF"] = "GeoTIFF::GeoTIFF"

        cmake.definitions["GDAL_USE_ARMADILLO"] = self.options.with_armadillo
        if self.options.with_armadillo:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_ARMADILLO"] = "armadillo"
            cmake.definitions["TARGET_FOR_ARMADILLO"] = \
                    self.dependencies["armadillo"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Armadillo_FOUND"] = False

        cmake.definitions["GDAL_USE_ARROW"] = self.options.with_arrow
        if self.options.with_arrow:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_ARROW"] = "arrow"
            cmake.definitions["TARGET_FOR_ARROW"] = \
                    self.dependencies["arrow"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Arrow_FOUND"] = False

        cmake.definitions["GDAL_USE_BLOSC"] = self.options.with_blosc
        if self.options.with_blosc:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_BLOSC"] = "c-blosc"
            cmake.definitions["TARGET_FOR_BLOSC"] = \
                    self.dependencies["c-blosc"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Blosc_FOUND"] = False

        cmake.definitions["GDAL_USE_CFITSIO"] = self.options.with_cfitsio
        if self.options.with_cfitsio:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_CFITSIO"] = "cfitsio"
            cmake.definitions["TARGET_FOR_CFITSIO"] = \
                    self.dependencies["cfitsio"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["CFITSIO_FOUND"] = False

        cmake.definitions["GDAL_USE_CRYPTOPP"] = self.options.with_cryptopp
        if self.options.with_cryptopp:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_CRYPTOPP"] = "cryptopp"
            cmake.definitions["TARGET_FOR_CRYPTOPP"] = \
                    self.dependencies["cryptopp"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["CryptoPP_FOUND"] = False

        cmake.definitions["GDAL_USE_CURL"] = self.options.with_curl
        if self.options.with_curl:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_CURL"] = "libcurl"
            cmake.definitions["TARGET_FOR_CURL"] = \
                    self.dependencies["libcurl"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["CURL_FOUND"] = False

        cmake.definitions["GDAL_USE_CRNLIB"] = self.options.with_dds
        if self.options.with_dds:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_CRNLIB"] = "crunch"
            cmake.definitions["TARGET_FOR_CRNLIB"] = \
                    self.dependencies["crunch"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Crnlib_FOUND"] = False

        cmake.definitions["GDAL_USE_EXPAT"] = self.options.with_expat
        if self.options.with_expat:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_EXPAT"] = "expat"
            cmake.definitions["TARGET_FOR_EXPAT"] = "EXPAT::EXPAT"
        else:
            cmake.definitions["EXPAT_FOUND"] = False

        cmake.definitions["GDAL_USE_OPENEXR"] = self.options.with_exr
        if self.options.with_exr:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_OPENEXR"] = "openexr"
            cmake.definitions["TARGET_FOR_OPENEXR"] = \
                    self.dependencies["openexr"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["OpenEXR_FOUND"] = False

        cmake.definitions["GDAL_USE_FREEXL"] = self.options.with_freexl
        if self.options.with_freexl:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_FREEXL"] = "freexl"
            cmake.definitions["TARGET_FOR_FREEXL"] = "freexl::freexl"
        else:
            cmake.definitions["FreeXL_FOUND"] = False

        cmake.definitions["GDAL_USE_GEOS"] = self.options.with_geos
        if self.options.with_geos:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_GEOS"] = "geos"
            cmake.definitions["TARGET_FOR_GEOS"] = \
                    self.dependencies["geos"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["GEOS_FOUND"] = False

        cmake.definitions["GDAL_USE_GIF"] = self.options.with_gif
        if self.options.with_gif:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_GIF"] = "giflib"
            cmake.definitions["TARGET_FOR_GIF"] = \
                    self.dependencies["giflib"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["GIF_FOUND"] = False

        cmake.definitions["GDAL_USE_GTA"] = self.options.with_gta
        if self.options.with_gta:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_GTA"] = "libgta"
            cmake.definitions["TARGET_FOR_GTA"] = \
                    self.dependencies["libgta"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["GTA_FOUND"] = False

        cmake.definitions["GDAL_USE_HDF4"] = self.options.with_hdf4
        if self.options.with_hdf4:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_HDF4"] = "hdf4"
            cmake.definitions["TARGET_FOR_HDF4"] = \
                    self.dependencies["hdf4"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["HDF4_FOUND"] = False

        cmake.definitions["GDAL_USE_HDF5"] = self.options.with_hdf5
        if self.options.with_hdf5:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_HDF5"] = "hdf5"
            cmake.definitions["TARGET_FOR_HDF5"] = \
                    self.dependencies["hdf5"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["HDF5_FOUND"] = False

        cmake.definitions["GDAL_USE_HEIF"] = self.options.with_heif
        if self.options.with_heif:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_HEIF"] = "libheif"
            cmake.definitions["TARGET_FOR_HEIF"] = \
                    self.dependencies["libheif"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["HEIF_FOUND"] = False

        cmake.definitions["GDAL_USE_KEA"] = self.options.with_kea
        if self.options.with_kea:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_KEA"] = "kealib"
            cmake.definitions["TARGET_FOR_KEA"] = \
                    self.dependencies["kealib"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["KEA_FOUND"] = False

        cmake.definitions["GDAL_USE_DEFLATE"] = self.options.with_libdeflate
        if self.options.with_libdeflate:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_DEFLATE"] = "libdeflate"
            cmake.definitions["TARGET_FOR_DEFLATE"] = \
                    self.dependencies["libdeflate"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Deflate_FOUND"] = False

        cmake.definitions["GDAL_USE_ICONV"] = self.options.with_libiconv
        if self.options.with_libiconv:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_ICONV"] = "libiconv"
            cmake.definitions["TARGET_FOR_ICONV"] = \
                    self.dependencies["libiconv"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Iconv_FOUND"] = False

        if self.options.with_jpeg == "libjpeg" or self.options.with_jpeg == "libjpeg-turbo":
            print(f'self.options.with_jpeg: {self.options.with_jpeg}')
            cmake.definitions["GDAL_USE_JPEG"] = True
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_JPEG"] = self.options.with_jpeg
            cmake.definitions["TARGET_FOR_JPEG"] = \
                    "JPEG::JPEG" if self.options.with_jpeg == "libjpeg" else "libjpeg-turbo::libjpeg-turbo"
        else:
            cmake.definitions["JPEG_FOUND"] = False

        cmake.definitions["GDAL_USE_LIBKML"] = self.options.with_libkml
        if self.options.with_libkml:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_LIBKML"] = "libkml"
            cmake.definitions["TARGET_FOR_LIBKML"] = \
                    self.dependencies["libkml"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["LibKML_FOUND"] = False

        cmake.definitions["GDAL_USE_TIFF"] = self.options.with_libtiff
        if self.options.with_libtiff:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_TIFF"] = "libtiff"
            cmake.definitions["TARGET_FOR_TIFF"] = \
                    self.dependencies["libtiff"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["TIFF_FOUND"] = False

        cmake.definitions["GDAL_USE_LZ4"] = self.options.with_lz4
        if self.options.with_lz4:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_LZ4"] = "lz4"
            cmake.definitions["TARGET_FOR_LZ4"] = \
                    self.dependencies["lz4"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["LZ4_FOUND"] = False

        cmake.definitions["GDAL_USE_MONGOCXX"] = self.options.with_mongocxx
        if self.options.with_mongocxx:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_MONGOCXX"] = "mongo-cxx-driver"
            cmake.definitions["TARGET_FOR_MONGOCXX"] = \
                    self.dependencies["mongo-cxx-driver"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["MONGOCXX_FOUND"] = False

        if self.options.with_mysql == "libmysqlclient" or self.options.with_mysql == "mariadb-connector-c":
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_MYSQL"] = str(self.options.with_mysql)
            cmake.definitions["TARGET_FOR_MYSQL"] = \
                    "mariadb-connector-c::mariadb-connector-c" \
                    if self.options.with_mysql == "mariadb-connector-c" \
                    else "libmysqlclient::libmysqlclient"
        else:
            cmake.definitions["MYSQL_FOUND"] = False

        cmake.definitions["GDAL_USE_NETCDF"] = self.options.with_netcdf
        if self.options.with_netcdf:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_NETCDF"] = "netcdf"
            cmake.definitions["TARGET_FOR_NETCDF"] = \
                    self.dependencies["netcdf"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["NetCDF_FOUND"] = False

        cmake.definitions["GDAL_USE_ODBC"] = self.options.with_odbc
        if self.options.with_odbc:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_ODBC"] = "odbc"
            cmake.definitions["TARGET_FOR_ODBC"] = \
                    self.dependencies["odbc"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["ODBC_FOUND"] = False

        cmake.definitions["GDAL_USE_OPENJPEG"] = self.options.with_openjpeg
        if self.options.with_openjpeg:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_OPENJPEG"] = "openjpeg"
            cmake.definitions["TARGET_FOR_OPENJPEG"] = \
                    self.dependencies["openjpeg"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["OPENJPEG_FOUND"] = False

        cmake.definitions["GDAL_USE_OPENSSL"] = self.options.with_openssl
        if self.options.with_openssl:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_OPENSSL"] = "openssl"
            cmake.definitions["TARGET_FOR_OPENSSL"] = \
                    self.dependencies["openssl"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["OpenSSL_FOUND"] = False

        cmake.definitions["GDAL_USE_PCRE"] = self.options.with_pcre
        if self.options.with_pcre:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_PCRE"] = "pcre"
            cmake.definitions["TARGET_FOR_PCRE"] = \
                    self.dependencies["pcre"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["PCRE_FOUND"] = False

        cmake.definitions["GDAL_USE_PDFIUM"] = self.options.with_pcre2
        if self.options.with_pcre2:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_PDFIUM"] = "pcre2"
            cmake.definitions["TARGET_FOR_PDFIUM"] = \
                    self.dependencies["pcre2"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["PDFIUM_FOUND"] = False

        cmake.definitions["GDAL_USE_POSTGRESQL"] = self.options.with_pg
        if self.options.with_pg:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_POSTGRESQL"] = "libpq"
            cmake.definitions["TARGET_FOR_POSTGRESQL"] = \
                    self.dependencies["libpq"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["PostgreSQL_FOUND"] = False

        cmake.definitions["GDAL_USE_PNG"] = self.options.with_png
        if self.options.with_png:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_PNG"] = "libpng"
            cmake.definitions["TARGET_FOR_PNG"] = \
                    self.dependencies["libpng"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["PNG_FOUND"] = False

        cmake.definitions["GDAL_USE_PODOFO"] = self.options.with_podofo
        if self.options.with_podofo:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_PODOFO"] = "podofo"
            cmake.definitions["TARGET_FOR_PODOFO"] = \
                    self.dependencies["podofo"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Podofo_FOUND"] = False

        cmake.definitions["GDAL_USE_POPPLER"] = self.options.with_poppler
        if self.options.with_poppler:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_POPPLER"] = "poppler"
            cmake.definitions["TARGET_FOR_POPPLER"] = \
                    self.dependencies["poppler"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["Poppler_FOUND"] = False

        cmake.definitions["GDAL_USE_PROJ"] = self.options.with_proj
        if self.options.with_proj:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_PROJ"] = "proj"
            cmake.definitions["TARGET_FOR_PROJ"] = \
                    self.dependencies["proj"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["PROJ_FOUND"] = False

        cmake.definitions["GDAL_USE_QHULL"] = self.options.with_qhull
        if self.options.with_qhull:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_QHULL"] = "qhull"
            cmake.definitions["TARGET_FOR_QHULL"] = \
                    self.dependencies["qhull"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["QHULL_FOUND"] = False

        cmake.definitions["GDAL_USE_SQLITE3"] = self.options.with_sqlite3
        if self.options.with_sqlite3:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_SQLITE3"] = "sqlite3"
            cmake.definitions["TARGET_FOR_SQLITE3"] = \
                    self.dependencies["sqlite3"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["SQLite3_FOUND"] = False

        cmake.definitions["GDAL_USE_WEBP"] = self.options.with_webp
        if self.options.with_webp:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_WEBP"] = "libwebp"
            cmake.definitions["TARGET_FOR_WEBP"] = \
                    self.dependencies["libwebp"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["WebP_FOUND"] = False

        cmake.definitions["GDAL_USE_XERCESC"] = self.options.with_xerces
        if self.options.with_xerces:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_XERCESC"] = "xerces-c"
            cmake.definitions["TARGET_FOR_XERCESC"] = \
                    self.dependencies["xerces-c"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["XercesC_FOUND"] = False

        cmake.definitions["GDAL_USE_LIBXML2"] = self.options.with_xml2
        if self.options.with_xml2:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_LIBXML2"] = "libxml2"
            cmake.definitions["TARGET_FOR_LIBXML2"] = \
                    self.dependencies["libxml2"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["LibXml2_FOUND"] = False

        cmake.definitions["GDAL_USE_ZLIB"] = self.options.with_zlib
        if self.options.with_zlib:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_ZLIB"] = "zlib"
            cmake.definitions["TARGET_FOR_ZLIB"] = \
                    self.dependencies["zlib"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["ZLIB_FOUND"] = False

        cmake.definitions["GDAL_USE_ZSTD"] = self.options.with_zstd
        if self.options.with_zstd:
            cmake.definitions["GDAL_CONAN_PACKAGE_FOR_ZSTD"] = "zstd"
            cmake.definitions["TARGET_FOR_ZSTD"] = \
                    self.dependencies["zstd"].cpp_info.get_property("cmake_target_name")
        else:
            cmake.definitions["ZSTD_FOUND"] = False


        for k, v in cmake.definitions.items():
            print(k, " = ", v)

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()

        cmake.build()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):

        self.cpp_info.set_property("cmake_file_name", "GDAL")
        self.cpp_info.set_property("cmake_target_name", "GDAL::GDAL")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "gdal")

        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "GDAL"

        lib_suffix = ""
        if is_msvc(self):
            if self.options.shared:
                lib_suffix += "_i"
            if self.settings.build_type == "Debug":
                lib_suffix += "_d"
        self.cpp_info.libs = ["gdal{}".format(lib_suffix)]

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
            self.cpp_info.requires.extend(['libjpeg-turbo::jpeg'])

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
            self.cpp_info.requires.extend(['pcre2::pcre2'])

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
        self.output.info(
            "Prepending to GDAL_DATA environment variable: {}".format(
                gdal_data_path))
        self.runenv_info.prepend_path("GDAL_DATA", gdal_data_path)
        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.GDAL_DATA = gdal_data_path

        if self.options.tools:
            self.buildenv_info.prepend_path("GDAL_DATA", gdal_data_path)
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(
                "Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
