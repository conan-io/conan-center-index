from conan import ConanFile
from conan.tools.files import apply_conandata_patches, get
from conan.tools.files.files import rmdir
from conans import CMake
import os
import re


def _strip_version(package):
    return re.sub(r"/.*", "", package)


def _option_name(dep):
    if "option" in dep:
        return dep["option"]
    return "with_" + _strip_version(dep["require"])


def _make_options(gdal_deps):
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False]
    }
    for dep in gdal_deps:
        if "require" in dep:
            options[_option_name(dep)] = [True, False]
    return options


def _make_default_options(gdal_deps):
    default_options = {"shared": False, "fPIC": True, "tools": False}
    for dep in gdal_deps:
        if "require" in dep:
            default_options[_option_name(dep)] = ("default" in dep
                                                  and dep["default"])

    return default_options


def _components(gdal_dep):
    if "conan_dep" in gdal_dep:
        d = gdal_dep["conan_dep"]
        return d if isinstance(d, list) else [d]
    package = _strip_version(gdal_dep["require"])
    return [ f"{package}::{package}" ]


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

    # List taken from cmake/helpers/CheckDependentLibraries.cmake within gdal sources
    # with the command:
    # grep -E '^[ \t]*gdal_check_package\(' cmake/helpers/CheckDependentLibraries.cmake \
    #   | sed 's/[ \t]*gdal_check_package(\([a-zA-Z_0-9]\+\) "\(.*\)"\(.*\)/{ 'dep': \'\1\', 'descr': \'\2\' },/' \
    #   | sort | uniq
    #
    #   'PROJ' has been added manually.

    gdal_deps = [{
        "conan_dep": "proj::projlib",
        "require": "proj/9.0.0",
        "dep": "PROJ",
        "default": True
    }, {
        "dep": "Armadillo",
        "require": "armadillo/10.7.3",
        "descr": "C++ library for linear algebra (used for TPS transformation)"
    }, {
        "dep": "Arrow",
        "conan_dep": "arrow::libarrow",
        "require": "arrow/8.0.0",
        "descr": "Apache Arrow C++ library"
    }, {
        "dep": "BRUNSLI",
        "descr": "Enable BRUNSLI for JPEG packing in MRF"
    }, {
        "require": "c-blosc/1.21.1",
        "option": "blosc",
        "dep": "Blosc",
        "descr": "Blosc compression"
    }, {
        "require": "cfitsio/4.1.0",
        "dep": "CFITSIO",
        "descr": "C FITS I/O library"
    }, {
        "conan_dep": "libcurl::curl",
        "require": "libcurl/7.83.1",
        "dep": "CURL",
        "descr": "Enable drivers to use web API"
    }, {
        "dep": "Crnlib",
        "descr": "enable gdal_DDS driver"
    }, {
        "require": "cryptopp/8.6.0",
        "conan_dep": "cryptopp::libcryptopp",
        "dep": "CryptoPP",
        "descr": "Use crypto++ library for CPL."
    }, {
        "require": "libdeflate/1.12",
        "default": True,
        "dep": "Deflate",
        "descr": "Enable libdeflate compression library (complement to ZLib)"
    }, {
        "dep": "ECW",
        "descr": "Enable ECW driver"
    }, {
        "require": "expat/2.4.8",
        "dep": "EXPAT",
        "descr": "Read and write XML formats"
    }, {
        "dep": "FYBA",
        "descr": "enable ogr_SOSI driver"
    }, {
        "dep": "FileGDB",
        "descr": "Enable FileGDB (based on closed-source SDK) driver"
    }, {
        "dep": "FreeXL",
        "descr": "Enable XLS driver"
    }, {
        "conan_dep": "geos::geos_c",
        "require": "geos/3.11.0",
        "default": True,
        "dep": "GEOS",
        "descr": "Geometry Engine - Open Source (GDAL core dependency)"
    }, {
        "require": "giflib/5.2.1",
        "option": "gif",
        "default": True,
        "dep": "GIF",
        "descr": "GIF compression library (external)"
    }, {
        "dep": "GTA",
        "descr": "Enable GTA driver"
    }, {
        "require": "libgeotiff/1.7.1",
        "default": True,
        "dep": "GeoTIFF",
        "descr": "libgeotiff library (external)"
    }, {
        "dep": "HDF4",
        "descr": "Enable HDF4 driver"
    }, {
        "require": "hdf5/1.13.1",
        "conan_dep": "hdf5::hdf5_c",
        "dep": "HDF5",
        "descr": "Enable Hadoop File System through native library"
    }, {
        "dep": "HEIF",
        "descr": "HEIF >= 1.1"
    }, {
        "dep": "IDB",
        "descr": "enable ogr_IDB driver"
    }, {
        "require": "libiconv/1.17",
        "dep": "Iconv",
        "descr": "Character set recoding (used in GDAL portability library)"
    }, {
        "dep": "JPEG",
        "descr": "JPEG compression library (external)"
    }, {
        "require": "json-c/0.15",
        "default": True,
        "dep": "JSONC",
        "descr": "json-c library (external)"
    }, {
        "dep": "JXL",
        "descr": "JPEG-XL compression (when used with internal libtiff)"
    }, {
        "dep": "KDU",
        "descr": "Enable KAKADU"
    }, {
        "dep": "KEA",
        "descr": "Enable KEA driver"
    }, {
        "dep": "LERC",
        "descr": "Enable LERC (external)"
    }, {
        "dep": "LURATECH",
        "descr": "Enable JP2Lura driver"
    }, {
        "require": "lz4/1.9.3",
        "dep": "LZ4",
        "descr": "LZ4 compression"
    }, {
        "dep": "LibLZMA",
        "descr": "LZMA compression"
    }, {
        "require": "libxml2/2.9.14",
        "dep": "LibXml2",
        "descr": "Read and write XML formats"
    }, {
        "dep": "MONGOCXX",
        "descr": "Enable MongoDBV3 driver"
    }, {
        "dep": "MRSID",
        "descr": "MrSID raster SDK"
    }, {
        "dep": "MSSQL_NCLI",
        "descr": "MSSQL Native Client to enable bulk copy"
    }, {
        "dep": "MSSQL_ODBC",
        "descr": "MSSQL ODBC driver to enable bulk copy"
    }, {
        "dep": "MySQL",
        "descr": "MySQL"
    }, {
        "dep": "NetCDF",
        "descr": "Enable netCDF driver"
    }, {
        "dep": "ODBC",
        "descr": "Enable DB support through ODBC"
    }, {
        "dep": "ODBCCPP",
        "descr": "odbc-cpp library (external)"
    }, {
        "dep": "OGDI",
        "descr": "Enable ogr_OGDI driver"
    }, {
        "dep": "OpenCAD",
        "descr": "libopencad (external, used by OpenCAD driver)"
    }, {
        "dep": "OpenCL",
        "descr": "Enable OpenCL (may be used for warping)"
    }, {
        "dep": "OpenEXR",
        "descr": "OpenEXR >=2.2"
    }, {
        "require": "openssl/1.1.1o",
        "conan_dep": "openssl::ssl",
        "dep": "OpenSSL",
        "descr": "Use OpenSSL library"
    }, {
        "dep": "Oracle",
        "descr": "Enable Oracle OCI driver"
    }, {
        "dep": "PCRE",
        "descr": "Enable PCRE support for sqlite3"
    }, {
        "dep": "PCRE2",
        "descr": "Enable PCRE2 support for sqlite3"
    }, {
        "dep": "PDFIUM",
        "descr": "Enable PDF driver with Pdfium (read side)"
    }, {
        "require": "libpng/1.6.37",
        "default": True,
        "dep": "PNG",
        "descr": "PNG compression library (external)"
    }, {
        "dep": "Parquet",
        "descr": "Apache Parquet C++ library"
    }, {
        "dep": "Podofo",
        "descr": "Enable PDF driver with Podofo (read side)"
    }, {
        "require": "poppler/21.07.0",
        "conan_dep": "poppler::libpoppler",
        "dep": "Poppler",
        "descr": "Enable PDF driver with Poppler (read side)"
    }, {
        "conan_dep": "libpq::pq",
        "require": "libpq/14.2",
        "option": "with_pg",
        "dep": "PostgreSQL",
        "descr": ""
    }, {
        "conan_dep": "qhull::libqhull",
        "require": "qhull/8.0.1",
        "default": True,
        "dep": "QHULL",
        "descr": "Enable QHULL (external)"
    }, {
        "dep": "RASDAMAN",
        "descr": "enable rasdaman driver"
    }, {
        "dep": "RASTERLITE2",
        "descr": "Enable RasterLite2 support for sqlite3"
    }, {
        "dep": "SFCGAL",
        "descr": "gdal core supports ISO 19107:2013 and OGC Simple Features" \
                + " Access 1.2 for 3D operations"
    }, {
        "dep": "SPATIALITE",
        "descr": "Enable spatialite support for sqlite3"
    }, {
        "conan_dep": "sqlite3::sqlite",
        "require": "sqlite3/3.38.5",
        "default": True,
        "dep": "SQLite3",
        "descr": "Enable SQLite3 support (used by SQLite/Spatialite, GPKG, " \
                + "Rasterlite, MBTiles, etc.)"
    }, {
        "dep": "SWIG",
        "descr": "Enable language bindings"
    }, {
        "dep": "Shapelib",
        "descr": "Enable Shapelib support (not recommended, internal Shapelib" \
                + " is preferred)."
    }, {
        "dep": "TEIGHA",
        "descr": "Enable DWG and DGNv8 drivers"
    }, {
        "require": "libtiff/4.3.0",
        "dep": "TIFF",
        "default": True,
        "descr": "Support for the Tag Image File Format (TIFF)."
    }, {
        "dep": "TileDB",
        "descr": "enable TileDB driver"
    }, {
        "dep": "WebP",
        "descr": "WebP compression"
    }, {
        "dep": "XercesC",
        "descr": "Read and write XML formats (needed for GMLAS and ILI drivers)"
    }, {
        "require": "zlib/1.2.12",
        "default": True,
        "dep": "ZLIB",
        "descr": "zlib (external)"
    }, {
        "conan_dep": "zstd::zstdlib",
        "require": "zstd/1.5.2",
        "dep": "ZSTD",
        "descr": "ZSTD compression library"
    }, {
        "dep": "rdb",
        "descr": "enable RIEGL RDB library"
    },
    {
        "conan_dep": [ "libkml::kmldom", "libkml::kmlengine" ],
        "dep": "LibKML",
        "require": "libkml/1.3.0"
    }]

    options = _make_options(gdal_deps)
    default_options = _make_default_options(gdal_deps)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.with_sqlite3:
            self.options["sqlite3"].enable_column_metadata = True

        if self.options.shared:
            del self.options.fPIC

    def requirements(self):

        for dep in self.gdal_deps:
            if "require" in dep and getattr(self.options, _option_name(dep)):
                self.requires(dep["require"])

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)

        if "fPIC" in self.options and self.options.fPIC:
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
        del cmake.definitions["CMAKE_MODULE_PATH"]

        cmake.definitions["SQLite3_HAS_COLUMN_METADATA"] = \
            self.options["sqlite3"].enable_column_metadata

        cmake.definitions["SQLite3_HAS_RTREE"] = self.options[
            "sqlite3"].enable_rtree

        if self.options.with_hdf5:
            cmake.definitions["HDF5_C_LIBRARIES"] = "HDF5::C"
            cmake.definitions["HDF5_BUILD_SHARED_LIBS"] = self.options["hdf5"].shared

        for dep in self.gdal_deps:
            upper = dep["dep"].upper()
            enabled = "require" in dep and getattr(self.options,
                                                   _option_name(dep))
            cmake.definitions["GDAL_USE_" + upper] = enabled
            if enabled:
                cmake.definitions["GDAL_CONAN_PACKAGE_FOR_" + upper] = \
                       _strip_version(dep["require"])
            else:
                cmake.definitions[dep["dep"] + "_FOUND"] = False

        for k, v in cmake.definitions.items():
            print(k, " = ", v)

        cmake.configure()
        return cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()

        cmake.build()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):

        self.cpp_info.set_property("cmake_file_name", "GDAL")
        self.cpp_info.set_property("cmake_target_name", "GDAL::GDAL")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "gdal")

        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "GDAL"

        self.cpp_info.libs = ["gdal"]

        for dep in self.gdal_deps:
            if "require" in dep and getattr(self.options, _option_name(dep)):
                self.cpp_info.requires.extend(_components(dep))

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
