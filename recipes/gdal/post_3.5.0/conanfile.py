import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file

required_conan_version = ">=1.52.0"


class GdalConan(ConanFile):
    name = "gdal"
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OSGeo/gdal"
    topics = ("osgeo", "geospatial", "raster", "vector")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "with_armadillo": [True, False],
        "with_arrow": [True, False],
        "with_basisu": [True, False],
        "with_blosc": [True, False],
        "with_cfitsio": [True, False],
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
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_jxl": [True, False],
        "with_kea": [True, False],
        "with_lerc": [True, False],
        "with_libarchive": [True, False],
        "with_libcsf": [True, False],
        "with_libdeflate": [True, False],
        "with_libiconv": [True, False],
        "with_libkml": [True, False],
        "with_libtiff": ["deprecated", True, False],
        "with_lzma": [True, False],
        "with_lz4": [True, False],
        "with_mongocxx": [True, False],
        "with_mysql": [None, "libmysqlclient", "mariadb-connector-c"],
        "with_netcdf": [True, False],
        "with_odbc": [True, False],
        "with_opencad": [True, False],
        "with_openjpeg": [True, False],
        "with_openssl": [True, False],
        "with_pcre": [True, False],
        "with_pcre2": [True, False],
        "with_pdfium": [True, False],
        "with_pg": [True, False],
        "with_png": [True, False],
        "with_podofo": [True, False],
        "with_poppler": [True, False],
        "with_proj": [True, False],
        "with_qhull": [True, False],
        "with_rasterlite2": [True, False],
        "with_shapelib": [True, False],
        "with_spatialite": [True, False],
        "with_sqlite3": [True, False],
        "with_webp": [True, False],
        "with_xerces": [True, False],
        "with_xml2": [True, False],
        "with_zlib": ["deprecated", True, False],
        "with_zstd": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": False,
        "with_armadillo": False,
        "with_arrow": False,
        "with_basisu": False,
        "with_blosc": False,
        "with_cfitsio": False,
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
        "with_jpeg": "libjpeg",
        "with_jxl": False,
        "with_kea": False,
        "with_lerc": False,
        "with_libarchive": False,
        "with_libcsf": True,
        "with_libdeflate": True,
        "with_libiconv": True,
        "with_libkml": False,
        "with_libtiff": "deprecated",
        "with_lzma": False,
        "with_lz4": False,
        "with_mongocxx": False,
        "with_mysql": None,
        "with_netcdf": False,
        "with_odbc": False,
        "with_opencad": True,
        "with_openjpeg": False,
        "with_openssl": False,
        "with_pcre": False,
        "with_pcre2": False,
        "with_pdfium": False,
        "with_pg": False,
        "with_png": True,
        "with_podofo": False,
        "with_poppler": False,
        "with_proj": True,
        "with_qhull": True,
        "with_rasterlite2": False,
        "with_shapelib": True,
        "with_spatialite": False,
        "with_sqlite3": True,
        "with_webp": False,
        "with_xerces": False,
        "with_xml2": False,
        "with_zlib": "deprecated",
        "with_zstd": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)
        copy(self, "ConanFindPackage.cmake", src=os.path.join(self.recipe_folder, "cmake"), dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
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
        self.requires("libtiff/4.5.1")
        # Used in a public header here:
        # https://github.com/OSGeo/gdal/blob/v3.7.1/port/cpl_minizip_ioapi.h#L26
        self.requires("zlib/1.2.13", transitive_headers=True)
        if self.options.with_armadillo:
            self.requires("armadillo/12.2.0")
        if self.options.with_arrow:
            self.requires("arrow/12.0.0")
        if self.options.with_basisu:
            self.requires("libbasisu/1.15.0")
        if self.options.with_blosc:
            self.requires("c-blosc/1.21.4")
        if self.options.with_cfitsio:
            self.requires("cfitsio/4.2.0")
        if self.options.with_cryptopp:
            self.requires("cryptopp/8.7.0")
        if self.options.with_curl:
            self.requires("libcurl/8.2.0")
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
        if self.options.with_jxl:
            self.requires("libjxl/0.6.1")
        if self.options.with_kea:
            self.requires("kealib/1.4.14")
        if self.options.with_lerc:
            self.requires("lerc/4.0.0")
        if self.options.with_libarchive:
            self.requires("libarchive/3.6.2")
        if self.options.with_libdeflate:
            self.requires("libdeflate/1.18")
        if self.options.with_libiconv:
            self.requires("libiconv/1.17")
        if self.options.with_libkml:
            self.requires("libkml/1.3.0")
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.2")
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
        if self.options.with_pdfium:
            self.requires("pdfium/cci.20210730")
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
        if self.options.with_rasterlite2:
            self.requires("librasterlite2/1.1.0-beta1")
        if self.options.with_spatialite:
            self.requires("libspatialite/5.0.1")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.42.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.1")
        if self.options.with_xerces:
            self.requires("xerces-c/3.2.4")
        if self.options.with_xml2:
            self.requires("libxml2/2.11.4")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        # Use of external shapelib is not recommended and is currently broken.
        # https://github.com/OSGeo/gdal/issues/5711
        # if self.options.with_shapelib:
        #     self.requires("shapelib/1.5.0")

    def build_requirements(self):
        # https://github.com/conan-io/conan/issues/3482#issuecomment-662284561
        self.tool_requires("cmake/[>=3.18 <4]")

    def validate(self):
        if self.options.with_pcre and self.options.with_pcre2:
            raise ConanInvalidConfiguration("Enable either pcre or pcre2, not both")

        if self.options.with_sqlite3 and not self.dependencies["sqlite3"].options.enable_column_metadata:
            raise ConanInvalidConfiguration("gdql requires sqlite3:enable_column_metadata=True")

        if self.dependencies["libtiff"].options.jpeg != self.options.with_jpeg:
            msg = "libtiff:jpeg and gdal:with_jpeg must be set to the same value, either libjpeg or libjpeg-turbo."
            # For some reason, the ConanInvalidConfiguration message is not shown, only
            #     ERROR: At least two recipes provides the same functionality:
            #      - 'libjpeg' provided by 'libjpeg-turbo/2.1.2', 'libjpeg/9d'
            # So we print the error message manually.
            self.output.error(msg)
            raise ConanInvalidConfiguration(msg)

        if self.options.with_poppler and self.dependencies["poppler"].options.with_libjpeg != self.options.with_jpeg:
            msg = "poppler:with_libjpeg and gdal:with_jpeg must be set to the same value, either libjpeg or" " libjpeg-turbo."
            self.output.error(msg)
            raise ConanInvalidConfiguration(msg)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["GDAL_OBJECT_LIBRARIES_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)

        tc.cache_variables["BUILD_JAVA_BINDINGS"] = False
        tc.cache_variables["BUILD_CSHARP_BINDINGS"] = False
        tc.cache_variables["BUILD_PYTHON_BINDINGS"] = False
        tc.cache_variables["BUILD_APPS"] = self.options.tools
        tc.cache_variables["BUILD_TESTING"] = False

        tc.cache_variables["GDAL_USE_GEOTIFF_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_GIF_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_JPEG_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_JPEG12_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_JSONC_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_LERC_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_PNG_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_QHULL_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_TIFF_INTERNAL"] = False
        tc.cache_variables["GDAL_USE_ZLIB_INTERNAL"] = False

        tc.cache_variables["GDAL_USE_LIBCSF_INTERNAL"] = self.options.with_libcsf
        tc.cache_variables["GDAL_USE_OPENCAD_INTERNAL"] = self.options.with_opencad
        tc.cache_variables["GDAL_USE_SHAPELIB_INTERNAL"] = self.options.with_shapelib

        tc.cache_variables["SQLite3_HAS_COLUMN_METADATA"] = self.dependencies["sqlite3"].options.enable_column_metadata
        tc.cache_variables["SQLite3_HAS_RTREE"] = self.dependencies["sqlite3"].options.enable_rtree

        tc.cache_variables["GDAL_USE_ARCHIVE"] = self.options.with_libarchive
        tc.cache_variables["GDAL_USE_ARMADILLO"] = self.options.with_armadillo
        tc.cache_variables["GDAL_USE_ARROW"] = self.options.with_arrow
        tc.cache_variables["GDAL_USE_ARROWDATASET"] = self.options.with_arrow
        tc.cache_variables["GDAL_USE_BASISU"] = self.options.with_basisu
        tc.cache_variables["GDAL_USE_BLOSC"] = self.options.with_blosc
        tc.cache_variables["GDAL_USE_CFITSIO"] = self.options.with_cfitsio
        tc.cache_variables["GDAL_USE_CRNLIB"] = self.options.with_dds
        tc.cache_variables["GDAL_USE_CRYPTOPP"] = self.options.with_cryptopp
        tc.cache_variables["GDAL_USE_CURL"] = self.options.with_curl
        tc.cache_variables["GDAL_USE_DEFLATE"] = self.options.with_libdeflate
        tc.cache_variables["GDAL_USE_EXPAT"] = self.options.with_expat
        tc.cache_variables["GDAL_USE_FREEXL"] = self.options.with_freexl
        tc.cache_variables["GDAL_USE_GEOS"] = self.options.with_geos
        tc.cache_variables["GDAL_USE_GEOTIFF"] = True
        tc.cache_variables["GDAL_USE_GIF"] = self.options.with_gif
        tc.cache_variables["GDAL_USE_GTA"] = self.options.with_gta
        tc.cache_variables["GDAL_USE_HDF4"] = self.options.with_hdf4
        tc.cache_variables["GDAL_USE_HDF5"] = self.options.with_hdf5
        tc.cache_variables["GDAL_USE_HEIF"] = self.options.with_heif
        tc.cache_variables["GDAL_USE_ICONV"] = self.options.with_libiconv
        tc.cache_variables["GDAL_USE_JSONC"] = True
        tc.cache_variables["GDAL_USE_JPEG"] = self.options.with_jpeg is not None
        tc.cache_variables["GDAL_USE_JXL"] = self.options.with_jxl
        tc.cache_variables["GDAL_USE_KEA"] = self.options.with_kea
        tc.cache_variables["GDAL_USE_LERC"] = self.options.with_lerc
        tc.cache_variables["GDAL_USE_LIBKML"] = self.options.with_libkml
        tc.cache_variables["GDAL_USE_LIBXML2"] = self.options.with_xml2
        tc.cache_variables["GDAL_USE_LZMA"] = self.options.with_lzma
        tc.cache_variables["GDAL_USE_LZ4"] = self.options.with_lz4
        tc.cache_variables["GDAL_USE_MONGOCXX"] = self.options.with_mongocxx
        tc.cache_variables["GDAL_USE_NETCDF"] = self.options.with_netcdf
        tc.cache_variables["GDAL_USE_ODBC"] = self.options.with_odbc
        tc.cache_variables["GDAL_USE_OPENEXR"] = self.options.with_exr
        tc.cache_variables["GDAL_USE_OPENJPEG"] = self.options.with_openjpeg
        tc.cache_variables["GDAL_USE_OPENSSL"] = self.options.with_openssl
        tc.cache_variables["GDAL_USE_PCRE"] = self.options.with_pcre
        tc.cache_variables["GDAL_USE_PCRE2"] = self.options.with_pcre2
        tc.cache_variables["GDAL_USE_PDFIUM"] = self.options.with_pdfium
        tc.cache_variables["GDAL_USE_PNG"] = self.options.with_png
        tc.cache_variables["GDAL_USE_PODOFO"] = self.options.with_podofo
        tc.cache_variables["GDAL_USE_POPPLER"] = self.options.with_poppler
        tc.cache_variables["GDAL_USE_POSTGRESQL"] = self.options.with_pg
        tc.cache_variables["GDAL_USE_PROJ"] = self.options.with_proj
        tc.cache_variables["GDAL_USE_QHULL"] = self.options.with_qhull
        tc.cache_variables["GDAL_USE_RASTERLITE2"] = self.options.with_rasterlite2
        tc.cache_variables["GDAL_USE_SHAPELIB"] = self.options.with_shapelib
        tc.cache_variables["GDAL_USE_SPATIALITE"] = self.options.with_spatialite
        tc.cache_variables["GDAL_USE_SQLITE3"] = self.options.with_sqlite3
        tc.cache_variables["GDAL_USE_TIFF"] = True
        tc.cache_variables["GDAL_USE_WEBP"] = self.options.with_webp
        tc.cache_variables["GDAL_USE_XERCESC"] = self.options.with_xerces
        tc.cache_variables["GDAL_USE_ZLIB"] = True
        tc.cache_variables["GDAL_USE_ZSTD"] = self.options.with_zstd
        tc.generate()

        jsonc = self.dependencies["json-c"]
        jsonc.cpp_info.includedirs.append(os.path.join(jsonc.package_folder, "include", "json-c"))

        deps = CMakeDeps(self)
        # Based on `grep -hPIR '(gdal_check_package|find_package2)\(' ~/.conan2/p/b/gdal*/b/src/cmake | sort -u`
        conan_to_cmake_pkg_name = {
            "armadillo": "Armadillo",
            "arrow": "Arrow",
            # "brunsli": "BRUNSLI",
            "c-blosc": "Blosc",
            "cfitsio": "CFITSIO",
            "crunch": "Crnlib",
            "cryptopp": "CryptoPP",
            # "ecw": "ECW",
            "expat": "EXPAT",
            # "filegdb": "FileGDB",
            "freexl": "FreeXL",
            # "fyba": "FYBA",
            "geos": "GEOS",
            "giflib": "GIF",
            "hdf4": "HDF4",
            "hdf5": "HDF5",
            # "hdfs": "HDFS",
            # "idb": "IDB",
            "json-c": "JSONC",
            # "kdu": "KDU",
            "kealib": "KEA",
            "lerc": "LERC",
            "libarchive": "ARCHIVE",
            "libbasisu": "basisu",
            # "libcsf": "LIBCSF",
            "libcurl": "CURL",
            "libdeflate": "Deflate",
            "libgeotiff": "GeoTIFF",
            "libgta": "GTA",
            "libheif": "HEIF",
            "libiconv": "Iconv",
            "libjpeg": "JPEG",
            "libjpeg-turbo": "JPEG",
            "libjxl": "JXL",
            "libkml": "LibKML",
            "libmysqlclient": "MySQL",
            "libpng": "PNG",
            "libpq": "PostgreSQL",
            # "libqb3": "libQB3",
            "librasterlite2": "RASTERLITE2",
            "libspatialite": "SPATIALITE",
            "libtiff": "TIFF",
            "libwebp": "WebP",
            "libxml2": "LibXml2",
            # "luratech": "LURATECH",
            "lz4": "LZ4",
            "mariadb-connector-c": "MySQL",
            "mongo-cxx-driver": "MONGOCXX",
            # "mrsid": "MRSID",
            # "mssql_ncli": "MSSQL_NCLI",
            # "mssql_odbc": "MSSQL_ODBC",
            "netcdf": "NetCDF",
            "odbc": "ODBC",
            # "odbccpp": "ODBCCPP",
            # "ogdi": "OGDI",
            # "opencad": "OpenCAD",
            # "opencl": "OpenCL",
            "openexr": "OpenEXR",
            "openjpeg": "OpenJPEG",
            "openssl": "OpenSSL",
            # "oracle": "Oracle",
            # "parquet": "Parquet",
            "pcre": "PCRE",
            "pcre2": "PCRE2",
            "pdfium": "PDFIUM",
            "podofo": "Podofo",
            "poppler": "Poppler",
            "proj": "PROJ",
            "qhull": "QHULL",
            # "rdb": "rdb",
            # "sfcgal": "SFCGAL",
            "shapelib": "Shapelib",
            "sqlite3": "SQLite3",
            # "teigha": "TEIGHA",
            # "tiledb": "TileDB",
            "xerces-c": "XercesC",
            "xz_utils": "LibLZMA",
            "zlib": "ZLIB",
            "zstd": "ZSTD",
        }
        for conan_name, cmake_name in conan_to_cmake_pkg_name.items():
            deps.set_property(conan_name, "cmake_find_mode", "config")
            deps.set_property(conan_name, "cmake_file_name", cmake_name)

        renamed_targets = {
            "arrow":                      "Arrow::arrow_shared",
            "c-blosc":                    "Blosc::Blosc",
            "cfitsio":                    "CFITSIO::CFITSIO",
            "crunch":                     "CRNLIB::Crnlib",
            "cryptopp":                   "CRYPTOPP::CRYPTOPP",
            "freexl":                     "FREEXL::freexl",
            "geos":                       "GEOS::GEOS",
            "hdf4":                       "HDF4::HDF4",
            "hdfs":                       "HDFS::HDFS",
            "kealib":                     "KEA::KEA",
            "lerc":                       "LERC::LERC",
            "libarchive":                 "ARCHIVE::ARCHIVE",
            "libbasisu":                  "basisu::basisu_lib",
            "libdeflate":                 "Deflate::Deflate",
            "libgeotiff":                 "GEOTIFF::GEOTIFF",
            "libheif":                    "HEIF::HEIF",
            "libjxl":                     "JXL::JXL",
            "librasterlite2":             "RASTERLITE2::RASTERLITE2",
            "libspatialite":              "SPATIALITE::SPATIALITE",
            "libwebp":                    "WEBP::WebP",
            "lz4":                        "LZ4::LZ4",
            "mongo-cxx-driver::bsoncxx":  "MONGOCXX::BSONCXX",
            "mongo-cxx-driver::mongocxx": "MONGOCXX::MONGOCXX",
            "netcds":                     "netCDF::netcdf",
            "openjpeg":                   "OPENJPEG::OpenJPEG",
            "pcre":                       "PCRE::PCRE",
            "pcre2::pcre2-8":             "PCRE2::PCRE2-8",
            "pdfium":                     "PDFIUM::PDFIUM",
            "podofo":                     "PODOFO::Podofo",
            "poppler":                    "Poppler::Poppler",
            "shapelib":                   "SHAPELIB::shp",
            "xz_utils":                   "LibLZMA::LibLZMA",
            "zstd":                       "ZSTD::zstd",
        }
        for component, new_target_name in renamed_targets.items():
            deps.set_property(component, "cmake_target_name", new_target_name)

        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "ConanFindPackage.cmake",
             src=self.export_sources_folder,
             dst=os.path.join(self.source_folder, "cmake", "helpers"))
        # Use standard target_link_libraries instead of gdal_target_link_libraries.
        # GDAL version does not allow PUBLIC and got stuck in an infinite recursion for some Conan deps.
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "helpers", "GdalDriverHelper.cmake"),
                        "function(gdal_target_link_libraries target)",
                        "function(gdal_target_link_libraries target)\ntarget_link_libraries(${target} ${ARGN})\nreturn()\n")
        # Fix Deflate::Deflate not being correctly propagated internally.
        replace_in_file(self, os.path.join(self.source_folder, "port", "CMakeLists.txt"),
                        "PRIVATE Deflate::Deflate",
                        "PUBLIC Deflate::Deflate")

    def build(self):
        self._patch_sources()
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

        libname = "gdal"
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                libname += "d"
        self.cpp_info.libs = [libname]

        self.cpp_info.requires.extend(["json-c::json-c"])
        self.cpp_info.requires.extend(["libgeotiff::libgeotiff"])
        self.cpp_info.requires.extend(["libtiff::libtiff"])
        self.cpp_info.requires.extend(["zlib::zlib"])
        if self.options.with_armadillo:
            self.cpp_info.requires.extend(["armadillo::armadillo"])
        if self.options.with_arrow:
            self.cpp_info.requires.extend(["arrow::libarrow"])
        if self.options.with_basisu:
            self.cpp_info.requires.extend(["libbasisu::libbasisu"])
        if self.options.with_blosc:
            self.cpp_info.requires.extend(["c-blosc::c-blosc"])
        if self.options.with_cfitsio:
            self.cpp_info.requires.extend(["cfitsio::cfitsio"])
        if self.options.with_cryptopp:
            self.cpp_info.requires.extend(["cryptopp::libcryptopp"])
        if self.options.with_curl:
            self.cpp_info.requires.extend(["libcurl::curl"])
        if self.options.with_dds:
            self.cpp_info.requires.extend(["crunch::crunch"])
        if self.options.with_expat:
            self.cpp_info.requires.extend(["expat::expat"])
        if self.options.with_exr:
            self.cpp_info.requires.extend(["openexr::openexr", "imath::imath"])
        if self.options.with_freexl:
            self.cpp_info.requires.extend(["freexl::freexl"])
        if self.options.with_geos:
            self.cpp_info.requires.extend(["geos::geos_c"])
        if self.options.with_gif:
            self.cpp_info.requires.extend(["giflib::giflib"])
        if self.options.with_gta:
            self.cpp_info.requires.extend(["libgta::libgta"])
        if self.options.with_hdf4:
            self.cpp_info.requires.extend(["hdf4::hdf4"])
        if self.options.with_hdf5:
            self.cpp_info.requires.extend(["hdf5::hdf5_c"])
        if self.options.with_heif:
            self.cpp_info.requires.extend(["libheif::libheif"])
        if self.options.with_jxl:
            self.cpp_info.requires.extend(["libjxl::libjxl"])
        if self.options.with_kea:
            self.cpp_info.requires.extend(["kealib::kealib"])
        if self.options.with_lerc:
            self.cpp_info.requires.extend(["lerc::lerc"])
        if self.options.with_libarchive:
            self.cpp_info.requires.extend(["libarchive::libarchive"])
        if self.options.with_libdeflate:
            self.cpp_info.requires.extend(["libdeflate::libdeflate"])
        if self.options.with_libiconv:
            self.cpp_info.requires.extend(["libiconv::libiconv"])
        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.requires.extend(["libjpeg::libjpeg"])
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.requires.extend(["libjpeg-turbo::turbojpeg"])
        if self.options.with_libkml:
            self.cpp_info.requires.extend(["libkml::kmldom", "libkml::kmlengine"])
        if self.options.with_lzma:
            self.cpp_info.requires.extend(["xz_utils::xz_utils"])
        if self.options.with_lz4:
            self.cpp_info.requires.extend(["lz4::lz4"])
        if self.options.with_mongocxx:
            self.cpp_info.requires.extend(["mongo-cxx-driver::mongo-cxx-driver"])
        if self.options.with_mysql == "libmysqlclient":
            self.cpp_info.requires.extend(["libmysqlclient::libmysqlclient"])
        elif self.options.with_mysql == "mariadb-connector-c":
            self.cpp_info.requires.extend(["mariadb-connector-c::mariadb-connector-c"])
        if self.options.with_netcdf:
            self.cpp_info.requires.extend(["netcdf::netcdf"])
        if self.options.with_odbc:
            self.cpp_info.requires.extend(["odbc::odbc"])
        if self.options.with_openjpeg:
            self.cpp_info.requires.extend(["openjpeg::openjpeg"])
        if self.options.with_openssl:
            self.cpp_info.requires.extend(["openssl::ssl"])
        if self.options.with_pcre:
            self.cpp_info.requires.extend(["pcre::pcre"])
        if self.options.with_pcre2:
            self.cpp_info.requires.extend(["pcre2::pcre2-8"])
        if self.options.with_pdfium:
            self.cpp_info.requires.extend(["pdfium::pdfium"])
        if self.options.with_pg:
            self.cpp_info.requires.extend(["libpq::pq"])
        if self.options.with_png:
            self.cpp_info.requires.extend(["libpng::libpng"])
        if self.options.with_podofo:
            self.cpp_info.requires.extend(["podofo::podofo"])
        if self.options.with_poppler:
            self.cpp_info.requires.extend(["poppler::libpoppler"])
        if self.options.with_proj:
            self.cpp_info.requires.extend(["proj::projlib"])
        if self.options.with_rasterlite2:
            self.cpp_info.requires.extend(["librasterlite2::librasterlite2"])
        if self.options.with_qhull:
            self.cpp_info.requires.extend(["qhull::libqhull"])
        if self.options.with_spatialite:
            self.cpp_info.requires.extend(["libspatialite::libspatialite"])
        if self.options.with_sqlite3:
            self.cpp_info.requires.extend(["sqlite3::sqlite"])
        if self.options.with_webp:
            self.cpp_info.requires.extend(["libwebp::libwebp"])
        if self.options.with_xerces:
            self.cpp_info.requires.extend(["xerces-c::xerces-c"])
        if self.options.with_xml2:
            self.cpp_info.requires.extend(["libxml2::libxml2"])
        if self.options.with_zstd:
            self.cpp_info.requires.extend(["zstd::zstdlib"])

        gdal_data_path = os.path.join(self.package_folder, "res", "gdal")
        self.output.info(f"Prepending to GDAL_DATA environment variable: {gdal_data_path}")
        self.runenv_info.prepend_path("GDAL_DATA", gdal_data_path)

        if self.options.tools:
            self.buildenv_info.prepend_path("GDAL_DATA", gdal_data_path)

        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "GDAL"
        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.GDAL_DATA = gdal_data_path
