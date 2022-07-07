from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, cmake_layout
from conans import CMake, tools
import os

class GdalConan(ConanFile):
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    topics = ("osgeo", "geospatial", "raster", "vector")
    homepage = "https://github.com/OSGeo/gdal"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd_intrinsics": [None, "sse", "ssse3", "avx"],
        "threadsafe": [True, False],
        "tools": [True, False],
        "with_libdeflate": [True, False],
        "with_libiconv": [True, False],
        "with_zstd": [True, False],
        "with_blosc": [True, False],
        "with_lz4": [True, False],
        "with_pg": [True, False],
        # "with_libgrass": [True, False],
        "with_cfitsio": [True, False],
        "with_pcraster": [True, False],
        "with_png": [True, False],
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
        "with_sqlite3": [True, False],
        # "with_rasterlite2": [True, False],
        "with_pcre": [True, False],
        "with_pcre2": [True, False],
        "with_webp": [True, False],
        "with_geos": [True, False],
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
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd_intrinsics": "sse",
        "threadsafe": True,
        "tools": False,
        "with_libdeflate": True,
        "with_libiconv": True,
        "with_zstd": False,
        "with_blosc": False,
        "with_lz4": False,
        "with_pg": False,
        # "with_libgrass": False,
        "with_cfitsio": False,
        "with_pcraster": True,
        "with_png": True,
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
        "with_sqlite3": True,
        # "with_rasterlite2": False,
        "with_pcre": False,
        "with_pcre2": False,
        "with_webp": False,
        "with_geos": True,
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
        self.requires("json-c/0.15")
        self.requires("libgeotiff/1.7.1")
        self.requires("libtiff/4.3.0")
        self.requires("proj/9.0.0")
        self.requires("libpng/1.6.37")
        self.requires("zlib/1.2.12")

        if self.options.get_safe("with_libdeflate"):
            self.requires("libdeflate/1.12")
        if self.options.with_libiconv:
            self.requires("libiconv/1.17")
        if self.options.get_safe("with_zstd"):
            self.requires("zstd/1.5.2")
        if self.options.get_safe("with_blosc"):
            self.requires("c-blosc/1.21.1")
        if self.options.get_safe("with_lz4"):
            self.requires("lz4/1.9.3")
        if self.options.with_pg:
            self.requires("libpq/14.2")
        # if self.options.with_libgrass:
        #     self.requires("libgrass/x.x.x")
        if self.options.with_cfitsio:
            self.requires("cfitsio/4.1.0")
        # if self.options.with_pcraster:
        #     self.requires("pcraster-rasterformat/1.3.2")
        if self.options.with_dds:
            self.requires("crunch/cci.20190615")
        if self.options.with_gta:
            self.requires("libgta/1.2.1")
        # if self.options.with_pcidsk:
        #     self.requires("pcidsk/x.x.x")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")
        if self.options.with_charls:
            self.requires("charls/2.3.4")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        # if self.options.with_ogdi:
        #     self.requires("ogdi/4.1.0")
        # if self.options.with_sosi:
        #     self.requires("fyba/4.1.1")
        if self.options.with_mongocxx:
            self.requires("mongo-cxx-driver/3.6.6")
        if self.options.with_hdf4:
            self.requires("hdf4/4.2.15")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.1")
        if self.options.with_kea:
            self.requires("kealib/1.4.14")
        if self.options.with_netcdf:
            self.requires("netcdf/4.8.1")
        if self.options.with_jasper:
            self.requires("jasper/2.0.33")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        # if self.options.with_fgdb:
        #     self.requires("file-geodatabase-api/x.x.x")
        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.0.29")
        elif self.options.with_mysql == "mariadb-connector-c":
            self.requires("mariadb-connector-c/3.1.12")
        if self.options.with_xerces:
            self.requires("xerces-c/3.2.3")
        if self.options.with_expat:
            self.requires("expat/2.4.8")
        if self.options.with_libkml:
            self.requires("libkml/1.3.0")
        if self.options.with_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.9")
        # if self.options.with_dods_root:
        #     self.requires("libdap/3.20.6")
        if self.options.with_curl:
            self.requires("libcurl/7.83.1")
        if self.options.with_xml2:
            self.requires("libxml2/2.9.14")
        # if self.options.with_spatialite:
        #     self.requires("libspatialite/4.3.0a")
        if self.options.get_safe("with_sqlite3"):
            self.requires("sqlite3/3.38.5")
        # if self.options.with_rasterlite2:
        #     self.requires("rasterlite2/x.x.x")
        if self.options.get_safe("with_pcre"):
            self.requires("pcre/8.45")
        if self.options.get_safe("with_pcre2"):
            self.requires("pcre2/10.40")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")
        if self.options.with_geos:
            self.requires("geos/3.11.0")
        # if self.options.with_sfcgal:
        #     self.requires("sfcgal/1.3.7")
        if self.options.with_qhull:
            self.requires("qhull/8.0.1")
        if self.options.with_opencl:
            self.requires("opencl-headers/2022.01.04")
            self.requires("opencl-icd-loader/2022.01.04")
        if self.options.with_freexl:
            self.requires("freexl/1.0.6")
        if self.options.with_poppler:
            self.requires("poppler/21.07.0")
        if self.options.with_podofo:
            self.requires("podofo/0.9.7")
        # if self.options.with_pdfium:
        #     self.requires("pdfium/x.x.x")
        # if self.options.get_safe("with_tiledb"):
        #     self.requires("tiledb/2.0.2")
        # if self.options.with_rasdaman:
        #     self.requires("raslib/x.x.x")
        # if self.options.with_armadillo:
        #     self.requires("armadillo/9.880.1")
        if self.options.with_cryptopp:
            self.requires("cryptopp/8.6.0")
        if self.options.with_crypto:
            self.requires("openssl/1.1.1o")
        # if not self.options.without_lerc:
        #     self.requires("lerc/2.1") # TODO: use conan recipe (not possible yet because lerc API is broken for GDAL)
        if self.options.get_safe("with_exr"):
            self.requires("openexr/3.1.5")
        if self.options.get_safe("with_heif"):
            self.requires("libheif/1.12.0")

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
