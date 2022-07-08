from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, cmake_layout
from conans import CMake, tools
import os
import re

def _strip_version(package):
    return re.sub(r"/.*", "", package)

def _option_name(dep):
    if 'option' in dep:
        return dep['option']
    return "with_" + _strip_version(dep["conan_dep"])

def _make_options(gdal_deps):
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False]
    }
    for dep in gdal_deps:
        if "conan_dep" in dep:
            options[_option_name(dep)] = [True, False]
    return options

def _make_default_options(gdal_deps):
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": False
    }
    for dep in gdal_deps:
        if "conan_dep" in dep:
            default_options[_option_name(dep)] = ("default" in dep and dep["default"])
            
    return default_options

class GdalConan(ConanFile):
    name = "gdal"
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    topics = ("osgeo", "geospatial", "raster", "vector")
    homepage = "https://github.com/OSGeo/gdal"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake", 'cmake_find_package'

    # List taken from cmake/helpers/CheckDependentLibraries.cmake within gdal sources
    # with the command:
    # grep -E '^[ \t]*gdal_check_package\(' cmake/helpers/CheckDependentLibraries.cmake \
    #   | sed 's/[ \t]*gdal_check_package(\([a-zA-Z_0-9]\+\) "\(.*\)"\(.*\)/{ 'dep': \'\1\', 'descr': \'\2\' },/' \
    #   | sort | uniq

    gdal_deps = [
        { 'dep': 'Armadillo', 'descr': 'C++ library for linear algebra (used for TPS transformation)' },
        { 'dep': 'Arrow', 'descr': 'Apache Arrow C++ library' },
        { 'dep': 'BRUNSLI', 'descr': 'Enable BRUNSLI for JPEG packing in MRF' },
        { 'conan_dep': "c-blosc/1.21.1", 'option': 'blosc', 'dep': 'Blosc', 'descr': 'Blosc compression' },
        { 'conan_dep': "cfitsio/4.1.0", 'dep': 'CFITSIO', 'descr': 'C FITS I/O library' },
        { 'dep': 'CURL', 'descr': 'Enable drivers to use web API' },
        { 'dep': 'Crnlib', 'descr': 'enable gdal_DDS driver' },
        { 'dep': 'CryptoPP', 'descr': 'Use crypto++ library for CPL.' },
        { 'conan_dep': 'libdeflate/1.12', 'default': True, 'dep': 'Deflate', 'descr': 'Enable libdeflate compression library (complement to ZLib)' },
        { 'dep': 'ECW', 'descr': 'Enable ECW driver' },
        { 'dep': 'EXPAT', 'descr': 'Read and write XML formats' },
        { 'dep': 'FYBA', 'descr': 'enable ogr_SOSI driver' },
        { 'dep': 'FileGDB', 'descr': 'Enable FileGDB (based on closed-source SDK) driver' },
        { 'dep': 'FreeXL', 'descr': 'Enable XLS driver' },
        { 'conan_dep': "geos/3.11.0", 'default': True, 'dep': 'GEOS', 'targets': "CONAN_PKG::geos", 'descr': 'Geometry Engine - Open Source (GDAL core dependency)' },
        { 'conan_dep': "giflib/5.2.1", 'option': 'gif', 'default': True, 'targets': "CONAN_PKG::giflib", 'dep': 'GIF', 'descr': 'GIF compression library (external)' },
        { 'dep': 'GTA', 'descr': 'Enable GTA driver' },
        { 'conan_dep':"libgeotiff/1.7.1", 'default': True, 'targets': "CONAN_PKG::libgeotiff", 'dep': 'GeoTIFF', 'descr': 'libgeotiff library (external)' },
        { 'dep': 'HDF4', 'descr': 'Enable HDF4 driver' },
        { 'dep': 'HDF5', 'descr': 'Enable HDF5" COMPONENTS "C" "CXX' },
        { 'dep': 'HDFS', 'descr': 'Enable Hadoop File System through native library' },
        { 'dep': 'HEIF', 'descr': 'HEIF >= 1.1' },
        { 'dep': 'IDB', 'descr': 'enable ogr_IDB driver' },
        { 'conan_dep': "libiconv/1.17", 'dep': 'Iconv', 'descr': 'Character set recoding (used in GDAL portability library)' },
        { 'dep': 'JPEG', 'descr': 'JPEG compression library (external)' },
        { 'conan_dep': "json-c/0.15", 'default': True, 'targets': "CONAN_PKG::json-c", 'dep': 'JSONC', 'descr': 'json-c library (external)' },
        { 'dep': 'JXL', 'descr': 'JPEG-XL compression (when used with internal libtiff)' },
        { 'dep': 'KDU', 'descr': 'Enable KAKADU' },
        { 'dep': 'KEA', 'descr': 'Enable KEA driver' },
        { 'dep': 'LERC', 'descr': 'Enable LERC (external)' },
        { 'dep': 'LURATECH', 'descr': 'Enable JP2Lura driver' },
        { 'conan_dep': "lz4/1.9.3", 'dep': 'LZ4', 'descr': 'LZ4 compression' },
        { 'dep': 'LibLZMA', 'descr': 'LZMA compression' },
        { 'dep': 'LibXml2', 'descr': 'Read and write XML formats' },
        { 'dep': 'MONGOCXX', 'descr': 'Enable MongoDBV3 driver' },
        { 'dep': 'MRSID', 'descr': 'MrSID raster SDK' },
        { 'dep': 'MSSQL_NCLI', 'descr': 'MSSQL Native Client to enable bulk copy' },
        { 'dep': 'MSSQL_ODBC', 'descr': 'MSSQL ODBC driver to enable bulk copy' },
        { 'dep': 'MySQL', 'descr': 'MySQL' },
        { 'dep': 'NetCDF', 'descr': 'Enable netCDF driver' },
        { 'dep': 'ODBC', 'descr': 'Enable DB support through ODBC' },
        { 'dep': 'ODBCCPP', 'descr': 'odbc-cpp library (external)' },
        { 'dep': 'OGDI', 'descr': 'Enable ogr_OGDI driver' },
        { 'dep': 'OpenCAD', 'descr': 'libopencad (external, used by OpenCAD driver)' },
        { 'dep': 'OpenCL', 'descr': 'Enable OpenCL (may be used for warping)' },
        { 'dep': 'OpenEXR', 'descr': 'OpenEXR >=2.2' },
        { 'dep': 'OpenSSL', 'descr': 'Use OpenSSL library' },
        { 'dep': 'Oracle', 'descr': 'Enable Oracle OCI driver' },
        { 'dep': 'PCRE', 'descr': 'Enable PCRE support for sqlite3' },
        { 'dep': 'PCRE2', 'descr': 'Enable PCRE2 support for sqlite3' },
        { 'dep': 'PDFIUM', 'descr': 'Enable PDF driver with Pdfium (read side)' },
        { 'conan_dep': "libpng/1.6.37", 'default': True, 'targets': "CONAN_PKG::libpng", 'dep': 'PNG', 'descr': 'PNG compression library (external)' },
        { 'dep': 'Parquet', 'descr': 'Apache Parquet C++ library' },
        { 'dep': 'Podofo', 'descr': 'Enable PDF driver with Podofo (read side)' },
        { 'dep': 'Poppler', 'descr': 'Enable PDF driver with Poppler (read side)' },
        { 'conan_dep': "libpq/14.2", 'option': 'with_pg', 'dep': 'PostgreSQL', 'descr': '' },
        { 'conan_dep': "qhull/8.0.1", 'default': True, 'dep': 'QHULL', 'descr': 'Enable QHULL (external)' },
        { 'dep': 'RASDAMAN', 'descr': 'enable rasdaman driver' },
        { 'dep': 'RASTERLITE2', 'descr': 'Enable RasterLite2 support for sqlite3' },
        { 'dep': 'SFCGAL', 'descr': 'gdal core supports ISO 19107:2013 and OGC Simple Features Access 1.2 for 3D operations' },
        { 'dep': 'SPATIALITE', 'descr': 'Enable spatialite support for sqlite3' },
        { 'conan_dep': "sqlite3/3.38.5", 'default': True, 'dep': 'SQLite3', 'descr': 'Enable SQLite3 support (used by SQLite/Spatialite, GPKG, Rasterlite, MBTiles, etc.)' },
        { 'dep': 'SWIG', 'descr': 'Enable language bindings' },
        { 'dep': 'Shapelib', 'descr': 'Enable Shapelib support (not recommended, internal Shapelib is preferred).' },
        { 'dep': 'TEIGHA', 'descr': 'Enable DWG and DGNv8 drivers' },
        { 'conan_dep': "libtiff/4.3.0", 'dep': 'TIFF', 'default': True, 'descr': 'Support for the Tag Image File Format (TIFF).' },
        { 'dep': 'TileDB', 'descr': 'enable TileDB driver' },
        { 'dep': 'WebP', 'descr': 'WebP compression' },
        { 'dep': 'XercesC', 'descr': 'Read and write XML formats (needed for GMLAS and ILI drivers)' },
        { 'conan_dep':"zlib/1.2.12", 'default': True, 'dep': 'ZLIB', 'descr': 'zlib (external)' },
        { 'conan_dep': 'zstd/1.5.2', 'dep': 'ZSTD', 'descr': 'ZSTD compression library' },
        { 'dep': 'rdb', 'descr': 'enable RIEGL RDB library' }
    ]
    
    options = _make_options(gdal_deps)
    default_options = _make_default_options(gdal_deps)

    options__ = {
        # "with_libgrass": [True, False],
        "with_cfitsio": [True, False],
        "with_pcraster": [True, False],
        "with_dds": [True, False],
        "with_gta": [True, False],
        "with_pcidsk": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_charls": [True, False],
        "with_gif": [True, False],
        # "with_ogdi": [True, False],
        # "with_sosi": [True, False],
        "with_mongocxx": [True, False],
        "with_hdf4": [True, False],
        "with_hdf5": [True, False],
        "with_kea": [True, False],
        "with_netcdf": [True, False],
        "with_jasper": [True, False],
        "with_openjpeg": [True, False],
        # "with_fgdb": [True, False],
        "with_gnm": [True, False],
        "with_mysql": [None, "libmysqlclient", "mariadb-connector-c"],
        "with_xerces": [True, False],
        "with_expat": [True, False],
        "with_libkml": [True, False],
        "with_odbc": [True, False],
        # "with_dods_root": [True, False],
        "with_curl": [True, False],
        "with_xml2": [True, False],
        # "with_spatialite": [True, False],
        # "with_rasterlite2": [True, False],
        "with_pcre": [True, False],
        "with_pcre2": [True, False],
        "with_webp": [True, False],
        # "with_sfcgal": [True, False],
        "with_qhull": [True, False],
        "with_opencl": [True, False],
        "with_freexl": [True, False],
        "without_pam": [True, False],
        "with_poppler": [True, False],
        "with_podofo": [True, False],
        # "with_pdfium": [True, False],
        # "with_tiledb": [True, False],
        # "with_rasdaman": [True, False],
        "with_brunsli": [True, False],
        # "with_armadillo": [True, False],
        "with_cryptopp": [True, False],
        "with_crypto": [True, False],
        "without_lerc": [True, False],
        "with_null": [True, False],
        "with_exr": [True, False],
        "with_heif": [True, False],
    }
    default_options__ = {
        "shared": False,
        "fPIC": True,
        "tools": False,
        # "with_libgrass": False,
        "with_cfitsio": False,
        "with_pcraster": True,
        "with_dds": False,
        "with_gta": False,
        "with_pcidsk": True,
        "with_jpeg": "libjpeg",
        "with_charls": False,
        "with_gif": True,
        # "with_ogdi": False,
        # "with_sosi": False,
        "with_mongocxx": False,
        "with_hdf4": False,
        "with_hdf5": False,
        "with_kea": False,
        "with_netcdf": False,
        "with_jasper": False,
        "with_openjpeg": False,
        # "with_fgdb": False,
        "with_gnm": True,
        "with_mysql": None,
        "with_xerces": False,
        "with_expat": False,
        "with_libkml": False,
        "with_odbc": False,
        # "with_dods_root": False,
        "with_curl": False,
        "with_xml2": False,
        # "with_spatialite": False,
        # "with_rasterlite2": False,
        "with_pcre": False,
        "with_pcre2": False,
        "with_webp": False,
        # "with_sfcgal": False,
        "with_qhull": True,
        "with_opencl": False,
        "with_freexl": False,
        "without_pam": False,
        "with_poppler": False,
        "with_podofo": False,
        # "with_pdfium": False,
        # "with_tiledb": False,
        # "with_rasdaman": False,
        "with_brunsli": False,
        # "with_armadillo": False,
        "with_cryptopp": False,
        "with_crypto": False,
        "without_lerc": False,
        "with_null": False,
        "with_exr": False,
        "with_heif": False,
    }

    exports_sources = [ "CMakeLists.txt" ]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("proj/9.0.0")

        for dep in self.gdal_deps:
            if "conan_dep" in dep and getattr(self.options, _option_name(dep)):
                    self.requires(dep['conan_dep'])

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.fPIC:
            cmake.definitions["GDAL_OBJECT_LIBRARIES_POSITION_INDEPENDENT_CODE"] = True

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

        for dep in self.gdal_deps:
            upper = dep['dep'].upper()
            enabled = "conan_dep" in dep and getattr(self.options, _option_name(dep))
            cmake.definitions["GDAL_USE_" + upper] = enabled
            if enabled and "targets" in dep:
                cmake.definitions["GDAL_CHECK_PACKAGE_" + upper + "_TARGETS"] = dep["targets"]


        for k, v in cmake.definitions.items():
            print(k, " = ", v)

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()

        cmake.build()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib/pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib/cmake"))

    def package_info(self):

        # It would be better to use GDAL-targets.cmake generated by cmake,
        # but I do not know how to do that.
        self.cpp_info.set_property("cmake_file_name", "GDAL")
        self.cpp_info.set_property("cmake_target_name", "GDAL::GDAL")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "gdal")

        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.includedirs.append(os.path.join("include", "gdal"))

        self.cpp_info.libs = ["gdal"]

        gdal_data_path = os.path.join(self.package_folder, "res", "gdal")
        self.output.info("Prepending to GDAL_DATA environment variable: {}".format(gdal_data_path))
        self.runenv_info.prepend_path("GDAL_DATA", gdal_data_path)
        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.GDAL_DATA = gdal_data_path

        if self.options.tools:
            self.buildenv_info.prepend_path("GDAL_DATA", gdal_data_path)
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
