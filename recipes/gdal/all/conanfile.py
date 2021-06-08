from contextlib import contextmanager
import os

from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class GdalConan(ConanFile):
    name = "gdal"
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    topics = ("conan", "gdal", "osgeo", "geospatial", "raster", "vector")
    homepage = "https://github.com/OSGeo/gdal"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**"
    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd_intrinsics": [None, "sse", "ssse3", "avx"],
        "threadsafe": [True, False],
        "with_zlib": [True, False],
        "with_libdeflate": [True, False],
        "with_libiconv": [True, False],
        "with_zstd": [True, False],
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
        # "with_epsilon": [True, False],
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
        "with_zlib": True,
        "with_libdeflate": True,
        "with_libiconv": True,
        "with_zstd": False,
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
        # "with_epsilon": False,
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
        # "with_armadillo": False,
        "with_cryptopp": False,
        "with_crypto": False,
        "without_lerc": False,
        "with_null": False,
        "with_exr": False,
        "with_heif": False,
    }

    _autotools= None
    _nmake_args = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_with_exr_option(self):
        return tools.Version(self.version) >= "3.1.0"

    @property
    def _has_with_libdeflate_option(self):
        return tools.Version(self.version) >= "3.2.0"

    @property
    def _has_with_heif_option(self):
        return tools.Version(self.version) >= "3.2.0"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # if tools.Version(self.version) < "3.0.0":
        #     del self.options.with_tiledb
        if not self._has_with_exr_option:
            del self.options.with_exr
        if not self._has_with_libdeflate_option:
            del self.options.with_libdeflate
        if not self._has_with_heif_option:
            del self.options.with_heif

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            min_cppstd = 14 if self.options.with_charls else 11
            tools.check_min_cppstd(self, min_cppstd)
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.simd_intrinsics
        if self.options.without_lerc:
            del self.options.with_zstd
        # if self.options.with_spatialite:
        #     del self.options.with_sqlite3
        if not self.options.get_safe("with_sqlite3", False):
            del self.options.with_pcre
        if self.settings.compiler == "Visual Studio":
            del self.options.threadsafe
            del self.options.with_null
            del self.options.with_zlib # zlib and png are always used in nmake build,
            del self.options.with_png  # and it's not trivial to fix
        else:
            del self.options.with_libiconv
        if self.options.get_safe("with_libdeflate") and not self.options.get_safe("with_zlib", True):
            raise ConanInvalidConfiguration("gdal:with_libdeflate=True requires gdal:with_zlib=True")
        self._strict_options_requirements()

        # FIXME: Visual Studio 2015 & 2017 are supported but CI of CCI lacks several Win SDK components
        if tools.Version(self.version) >= "3.2.0" and self.settings.compiler == "Visual Studio" and \
           tools.Version(self.settings.compiler.version) < "16":
            raise ConanInvalidConfiguration("Visual Studio < 2019 not yet supported in this recipe for gdal {}".format(self.version))

    def _strict_options_requirements(self):
        if self.options.with_qhull:
            self.options["qhull"].reentrant = False

    def requirements(self):
        self.requires("json-c/0.15")
        self.requires("libgeotiff/1.6.0")
        # self.requires("libopencad/0.0.2") # TODO: use conan recipe when available instead of internal one
        self.requires("libtiff/4.2.0")
        self.requires("proj/8.0.1")
        if tools.Version(self.version) >= "3.1.0":
            self.requires("flatbuffers/1.12.0")
        if self.options.get_safe("with_zlib", True):
            self.requires("zlib/1.2.11")
        if self.options.get_safe("with_libdeflate"):
            self.requires("libdeflate/1.7")
        if self.options.get_safe("with_libiconv", True):
            self.requires("libiconv/1.16")
        if self.options.get_safe("with_zstd"):
            self.requires("zstd/1.5.0")
        if self.options.with_pg:
            self.requires("libpq/13.2")
        # if self.options.with_libgrass:
        #     self.requires("libgrass/x.x.x")
        if self.options.with_cfitsio:
            self.requires("cfitsio/3.490")
        # if self.options.with_pcraster:
        #     self.requires("pcraster-rasterformat/1.3.2")
        if self.options.get_safe("with_png", True):
            self.requires("libpng/1.6.37")
        if self.options.with_dds:
            self.requires("crunch/cci.20190615")
        if self.options.with_gta:
            self.requires("libgta/1.2.1")
        # if self.options.with_pcidsk:
        #     self.requires("pcidsk/x.x.x")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.0")
        if self.options.with_charls:
            self.requires("charls/2.1.0")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        # if self.options.with_ogdi:
        #     self.requires("ogdi/4.1.0")
        # if self.options.with_sosi:
        #     self.requires("fyba/4.1.1")
        if self.options.with_mongocxx:
            self.requires("mongo-cxx-driver/3.6.2")
        if self.options.with_hdf4:
            self.requires("hdf4/4.2.15")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.0")
        if self.options.with_kea:
            self.requires("kealib/1.4.14")
        if self.options.with_netcdf:
            self.requires("netcdf/4.7.4")
        if self.options.with_jasper:
            self.requires("jasper/2.0.32")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.4.0")
        # if self.options.with_fgdb:
        #     self.requires("file-geodatabase-api/x.x.x")
        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.0.17")
        elif self.options.with_mysql == "mariadb-connector-c":
            self.requires("mariadb-connector-c/3.1.12")
        if self.options.with_xerces:
            self.requires("xerces-c/3.2.3")
        if self.options.with_expat:
            self.requires("expat/2.4.1")
        if self.options.with_libkml:
            self.requires("libkml/1.3.0")
        if self.options.with_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.9")
        # if self.options.with_dods_root:
        #     self.requires("libdap/3.20.6")
        if self.options.with_curl:
            self.requires("libcurl/7.77.0")
        if self.options.with_xml2:
            self.requires("libxml2/2.9.10")
        # if self.options.with_spatialite:
        #     self.requires("libspatialite/4.3.0a")
        if self.options.get_safe("with_sqlite3"):
            self.requires("sqlite3/3.35.5")
        # if self.options.with_rasterlite2:
        #     self.requires("rasterlite2/x.x.x")
        if self.options.get_safe("with_pcre"):
            self.requires("pcre/8.44")
        # if self.options.with_epsilon:
        #     self.requires("epsilon/0.9.2")
        if self.options.with_webp:
            self.requires("libwebp/1.2.0")
        if self.options.with_geos:
            self.requires("geos/3.9.1")
        # if self.options.with_sfcgal:
        #     self.requires("sfcgal/1.3.7")
        if self.options.with_qhull:
            self.requires("qhull/8.0.1")
        if self.options.with_opencl:
            self.requires("opencl-headers/2021.04.29")
            self.requires("opencl-icd-loader/2021.04.29")
        if self.options.with_freexl:
            self.requires("freexl/1.0.6")
        if self.options.with_poppler:
            self.requires("poppler/20.09.0")
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
            self.requires("cryptopp/8.5.0")
        if self.options.with_crypto:
            self.requires("openssl/1.1.1k")
        # if not self.options.without_lerc:
        #     self.requires("lerc/2.1") # TODO: use conan recipe (not possible yet because lerc API is broken for GDAL)
        if self.options.get_safe("with_exr"):
            self.requires("openexr/2.5.5")
        if self.options.get_safe("with_heif"):
            self.requires("libheif/1.12.0")

    def validate(self):
        if self.options.with_qhull and self.options["qhull"].reentrant:
            raise ConanInvalidConfiguration("gdal depends on non-reentrant qhull.")

    def _validate_dependency_graph(self):
        if tools.Version(self.deps_cpp_info["libtiff"].version) < "4.0.0":
            raise ConanInvalidConfiguration("gdal {} requires libtiff >= 4.0.0".format(self.version))
        if self.options.with_mongocxx:
            mongocxx_version = tools.Version(self.deps_cpp_info["mongo-cxx-driver"].version)
            if mongocxx_version < "3.0.0":
                # TODO: handle mongo-cxx-driver v2
                raise ConanInvalidConfiguration("gdal with mongo-cxx-driver < 3.0.0 not yet supported in this recipe.")
            elif mongocxx_version < "3.4.0":
                raise ConanInvalidConfiguration("gdal with mongo-cxx-driver v3 requires 3.4.0 at least.")

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        # Remove embedded dependencies
        embedded_libs = [
            os.path.join("alg", "internal_libqhull"),
            os.path.join("frmts", "gif", "giflib"),
            os.path.join("frmts", "jpeg", "libjpeg"),
            os.path.join("frmts", "png", "libpng"),
            os.path.join("frmts", "zlib"),
            # os.path.join("ogr", "ogrsf_frmts", "cad", "libopencad"), # TODO: uncomment when libopencad available
            os.path.join("ogr", "ogrsf_frmts", "geojson", "libjson"),
        ]
        if tools.Version(self.version) >= "3.1.0":
            embedded_libs.append(os.path.join("ogr", "ogrsf_frmts", "flatgeobuf", "flatbuffers"))
        for lib_subdir in embedded_libs:
            tools.rmdir(os.path.join(self._source_subfolder, lib_subdir))

        # OpenCL headers
        tools.replace_in_file(os.path.join(self._source_subfolder, "alg", "gdalwarpkernel_opencl.h"),
                              "#include <OpenCL/OpenCL.h>",
                              "#include <CL/opencl.h>")

        # More patches for autotools build
        if self.settings.compiler != "Visual Studio":
            configure_ac = os.path.join(self._source_subfolder, "configure.ac")
            # Workaround for nc-config not packaged in netcdf recipe (gdal relies on it to check nc4 and hdf4 support in netcdf):
            if self.options.with_netcdf and self.options["netcdf"].netcdf4 and self.options["netcdf"].with_hdf5:
                tools.replace_in_file(configure_ac,
                                      "NETCDF_HAS_NC4=no",
                                      "NETCDF_HAS_NC4=yes")
            # Fix zlib checks and -lz injection to ensure to use external zlib and not fail others checks
            if self.options.get_safe("with_zlib", True):
                zlib_name = self.deps_cpp_info["zlib"].libs[0]
                tools.replace_in_file(configure_ac,
                                      "AC_CHECK_LIB(z,",
                                      "AC_CHECK_LIB({},".format(zlib_name))
                tools.replace_in_file(configure_ac,
                                      "-lz ",
                                      "-l{} ".format(zlib_name))
            # Workaround for autoconf 2.71
            with open(os.path.join(self._source_subfolder, "config.rpath"), "w"):
                pass

    def _edit_nmake_opt(self):
        simd_intrinsics = str(self.options.get_safe("simd_intrinsics", False))
        if simd_intrinsics != "avx":
            self._replace_in_nmake_opt("AVXFLAGS = /DHAVE_AVX_AT_COMPILE_TIME", "")
        if simd_intrinsics not in ["sse3", "avx"]:
            self._replace_in_nmake_opt("SSSE3FLAGS = /DHAVE_SSSE3_AT_COMPILE_TIME", "")
        if simd_intrinsics not in ["sse", "sse3", "avx"]:
            self._replace_in_nmake_opt("SSEFLAGS = /DHAVE_SSE_AT_COMPILE_TIME", "")
        if self.options.without_pam:
            self._replace_in_nmake_opt("PAM_SETTING=-DPAM_ENABLED", "")
        if not self.options.with_gnm:
            self._replace_in_nmake_opt("INCLUDE_GNM_FRMTS = YES", "")
        if not self.options.with_odbc:
            self._replace_in_nmake_opt("ODBC_SUPPORTED = 1", "")
        if not bool(self.options.with_jpeg):
            self._replace_in_nmake_opt("JPEG_SUPPORTED = 1", "")
        self._replace_in_nmake_opt("JPEG12_SUPPORTED = 1", "")
        if not self.options.with_pcidsk:
            self._replace_in_nmake_opt("PCIDSK_SETTING=INTERNAL", "")
        if self.options.with_pg:
            self._replace_in_nmake_opt("#PG_LIB = n:\\pkg\\libpq_win32\\lib\\libpqdll.lib wsock32.lib", "PG_LIB=")
        if bool(self.options.with_mysql):
            self._replace_in_nmake_opt("#MYSQL_LIB = D:\\Software\\MySQLServer4.1\\lib\\opt\\libmysql.lib advapi32.lib", "MYSQL_LIB=")
        if self.options.get_safe("with_sqlite3"):
            self._replace_in_nmake_opt("#SQLITE_LIB=N:\\pkg\\sqlite-win32\\sqlite3_i.lib", "SQLITE_LIB=")
        if self.options.with_curl:
            self._replace_in_nmake_opt("#CURL_LIB = $(CURL_DIR)/libcurl.lib wsock32.lib wldap32.lib winmm.lib", "CURL_LIB=")
        if self.options.with_freexl:
            self._replace_in_nmake_opt("#FREEXL_LIBS = e:/freexl-1.0.0a/freexl_i.lib", "FREEXL_LIBS=")
        if not (self.options.get_safe("with_zlib", True) and self.options.get_safe("with_png", True) and bool(self.options.with_jpeg)):
            self._replace_in_nmake_opt("MRF_SETTING=yes", "")
        if self.options.with_charls:
            self._replace_in_nmake_opt("#CHARLS_LIB=e:\\work\\GIS\gdal\\supportlibs\\charls\\bin\\Release\\x86\\CharLS.lib", "CHARLS_LIB=")
        # Inject required systems libs of dependencies
        self._replace_in_nmake_opt("ADD_LIBS	=", "ADD_LIBS={}".format(" ".join([lib + ".lib" for lib in self.deps_cpp_info.system_libs])))
        # Trick to enable OpenCL (option missing in upstream nmake files)
        if self.options.with_opencl:
            tools.replace_in_file(os.path.join(self._source_subfolder, "alg", "makefile.vc"),
                                  "$(GEOS_CFLAGS)", "$(GEOS_CFLAGS) /DHAVE_OPENCL")

    def _replace_in_nmake_opt(self, str1, str2):
        tools.replace_in_file(os.path.join(self.build_folder, self._source_subfolder, "nmake.opt"), str1, str2)

    def _get_nmake_args(self):
        if self._nmake_args:
            return self._nmake_args

        args = []
        args.append("GDAL_HOME=\"{}\"".format(self.package_folder))
        args.append("DATADIR=\"{}\"".format(os.path.join(self.package_folder, "res", "gdal")))
        if self.settings.arch == "x86_64":
            args.append("WIN64=1")
        args.append("DEBUG={}".format("1" if self.settings.build_type == "Debug" else "0"))
        args.append("DLLBUILD={}".format("1" if self.options.shared else "0"))
        args.append("PROJ_INCLUDE=\"-I{}\"".format(" -I".join(self.deps_cpp_info["proj"].include_paths)))
        if self.options.with_libiconv:
            args.append("LIBICONV_INCLUDE=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libiconv"].include_paths)))
            args.append("LIBICONV_CFLAGS=\"-DICONV_CONST=\"")
        args.append("JPEG_EXTERNAL_LIB=1")
        if self.options.with_jpeg == "libjpeg":
            args.append("JPEGDIR=\"{}\"".format(" -I".join(self.deps_cpp_info["libjpeg"].include_paths)))
        elif self.options.with_jpeg == "libjpeg-turbo":
            args.append("JPEGDIR=\"{}\"".format(" -I".join(self.deps_cpp_info["libjpeg-turbo"].include_paths)))
        args.append("PNG_EXTERNAL_LIB=1")
        args.append("PNGDIR=\"{}\"".format(" -I".join(self.deps_cpp_info["libpng"].include_paths)))
        if self.options.with_gif:
            args.append("GIF_SETTING=EXTERNAL")
        if self.options.with_pcraster:
            args.append("PCRASTER_SETTING=INTERNAL")
        args.append("TIFF_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libtiff"].include_paths)))
        args.append("GEOTIFF_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libgeotiff"].include_paths)))
        if self.options.with_libkml:
            args.append("LIBKML_DIR=\"{}\"".format(self.deps_cpp_info["libkml"].rootpath))
        if self.options.with_expat:
            args.append("EXPAT_DIR=\"{}\"".format(self.deps_cpp_info["expat"].rootpath))
            args.append("EXPAT_INCLUDE=\"-I{}\"".format(" -I".join(self.deps_cpp_info["expat"].include_paths)))
        if self.options.with_xerces:
            args.append("XERCES_DIR=\"{}\"".format(self.deps_cpp_info["xerces-c"].rootpath))
            args.append("XERCES_INCLUDE=\"-I{}\"".format(" -I".join(self.deps_cpp_info["xerces-c"].include_paths)))
        if self.options.with_jasper:
            args.append("JASPER_DIR=\"{}\"".format(self.deps_cpp_info["jasper"].rootpath))
        if self.options.with_hdf4:
            args.append("HDF4_DIR=\"{}\"".format(self.deps_cpp_info["hdf4"].rootpath))
            args.append("HDF4_INCLUDE=\"{}\"".format(" -I".join(self.deps_cpp_info["hdf4"].include_paths)))
            if tools.Version(self.deps_cpp_info["hdf4"].version) >= "4.2.5":
                args.append("HDF4_HAS_MAXOPENFILES=YES")
        if self.options.with_hdf5:
            args.append("HDF5_DIR=\"{}\"".format(self.deps_cpp_info["hdf5"].rootpath))
        if self.options.with_kea:
            args.append("KEA_CFLAGS=\"-I{}\"".format(" -I".join(self.deps_cpp_info["kealib"].include_paths)))
        if self.options.with_pg:
            args.append("PG_INC_DIR=\"{}\"".format(" -I".join(self.deps_cpp_info["libpq"].include_paths)))
        if self.options.with_mysql == "libmysqlclient":
            args.append("MYSQL_INC_DIR=\"{}\"".format(" -I".join(self.deps_cpp_info["libmysqlclient"].include_paths)))
        elif self.options.with_mysql == "mariadb-connector-c":
            args.append("MYSQL_INC_DIR=\"{}\"".format(" -I".join(self.deps_cpp_info["mariadb-connector-c"].include_paths)))
        if self.options.get_safe("with_sqlite3"):
            args.append("SQLITE_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["sqlite3"].include_paths)))
        if self.options.get_safe("with_pcre"):
            args.append("PCRE_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["pcre"].include_paths)))
        if self.options.with_cfitsio:
            args.append("FITS_INC_DIR=\"{}\"".format(" -I".join(self.deps_cpp_info["cfitsio"].include_paths)))
        if self.options.with_netcdf:
            args.extend([
                "NETCDF_SETTING=YES",
                "NETCDF_INC_DIR=\"{}\"".format(" -I".join(self.deps_cpp_info["netcdf"].include_paths))
            ])
            if self.options["netcdf"].netcdf4 and self.options["netcdf"].with_hdf5:
                args.append("NETCDF_HAS_NC4=YES")
        if self.options.with_curl:
            args.append("CURL_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libcurl"].include_paths)))
        if self.options.with_geos:
            args.append("GEOS_CFLAGS=\"-I{} -DHAVE_GEOS\"".format(" -I".join(self.deps_cpp_info["geos"].include_paths)))
        if self.options.with_openjpeg:
            args.append("OPENJPEG_ENABLED=YES")
        if self.options.get_safe("with_zlib", True):
            args.append("ZLIB_EXTERNAL_LIB=1")
            args.append("ZLIB_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["zlib"].include_paths)))
        if self.options.get_safe("with_libdeflate"):
            args.append("LIBDEFLATE_CFLAGS=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libdeflate"].include_paths)))
        if self.options.with_poppler:
            poppler_version = tools.Version(self.deps_cpp_info["poppler"].version)
            args.extend([
                "POPPLER_ENABLED=YES",
                "POPPLER_MAJOR_VERSION={}".format(poppler_version.major),
                "POPPLER_MINOR_VERSION={}".format(poppler_version.minor)
            ])
        if self.options.with_podofo:
            args.append("PODOFO_ENABLED=YES")
        if self.options.get_safe("with_zstd"):
            args.append("ZSTD_CFLAGS=\"-I{}\"".format(" -I".join(self.deps_cpp_info["zstd"].include_paths)))
        if self.options.with_webp:
            args.append("WEBP_ENABLED=YES")
            args.append("WEBP_CFLAGS=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libwebp"].include_paths)))
        if self.options.with_xml2:
            args.append("LIBXML2_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libxml2"].include_paths)))
        if self.options.with_gta:
            args.append("GTA_CFLAGS=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libgta"].include_paths)))
        if self.options.with_mongocxx:
            args.append("MONGOCXXV3_CFLAGS=\"-I{}\"".format(" -I".join(self.deps_cpp_info["mongo-cxx-driver"].include_paths)))
        args.append("QHULL_SETTING={}".format("EXTERNAL" if self.options.with_qhull else "NO"))
        if self.options.with_cryptopp:
            args.append("CRYPTOPP_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["cryptopp"].include_paths)))
            if self.options["cryptopp"].shared:
                args.append("USE_ONLY_CRYPTODLL_ALG=YES")
        if self.options.with_crypto:
            args.append("OPENSSL_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["openssl"].include_paths)))
        if self.options.without_lerc:
            args.append("HAVE_LERC=0")
        if self.options.with_charls:
            charls_version = tools.Version(self.deps_cpp_info["charls"].version)
            if charls_version >= "2.1.0":
                args.append("CHARLS_FLAGS=-DCHARLS_2_1")
            elif charls_version >= "2.0.0":
                args.append("CHARLS_FLAGS=-DCHARLS_2")
        if self.options.with_dds:
            args.append("CRUNCH_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["crunch"].include_paths)))
        if self.options.get_safe("with_exr"):
            args.append("EXR_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["openexr"].include_paths)))
        if self.options.get_safe("with_heif"):
            args.append("HEIF_INC=\"-I{}\"".format(" -I".join(self.deps_cpp_info["libheif"].include_paths)))

        self._nmake_args = args
        return self._nmake_args

    def _gather_libs(self, p):
        libs = self.deps_cpp_info[p].libs + self.deps_cpp_info[p].system_libs
        for dep in self.deps_cpp_info[p].public_deps:
            for l in self._gather_libs(dep):
                if not l in libs:
                    libs.append(l)
        return libs

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        args = []
        args.append("--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))))
        # Shared/Static
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        # Enable C++14 if requested in conan profile or if with_charls enabled
        if (self.settings.compiler.cppstd and tools.valid_min_cppstd(self, 14)) or self.options.with_charls:
            args.append("--with-cpp14")
        # Debug
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        # SIMD Intrinsics
        simd_intrinsics = self.options.get_safe("simd_intrinsics", False)
        if not simd_intrinsics:
            args.extend(["--without-sse", "--without-ssse3", "--without-avx"])
        elif simd_intrinsics == "sse":
            args.extend(["--with-sse", "--without-ssse3", "--without-avx"])
        elif simd_intrinsics == "ssse3":
            args.extend(["--with-sse", "--with-ssse3", "--without-avx"])
        elif simd_intrinsics == "avx":
            args.extend(["--with-sse", "--with-ssse3", "--with-avx"])
        # LTO (disabled)
        args.append("--disable-lto")
        # Symbols
        args.append("--with-hide_internal_symbols")
        # Do not add /usr/local/lib and /usr/local/include
        args.append("--without-local")
        # Threadsafe
        args.append("--with-threads={}".format("yes" if self.options.threadsafe else "no"))
        # Depencencies:
        args.append("--with-proj=yes") # always required !
        args.append("--with-libz={}".format("yes" if self.options.with_zlib else "no"))
        if self._has_with_libdeflate_option:
            args.append("--with-libdeflate={}".format("yes" if self.options.with_libdeflate else "no"))
        args.append("--with-libiconv-prefix={}".format(tools.unix_path(self.deps_cpp_info["libiconv"].rootpath)))
        args.append("--with-liblzma=no") # always disabled: liblzma is an optional transitive dependency of gdal (through libtiff).
        args.append("--with-zstd={}".format("yes" if self.options.get_safe("with_zstd") else "no")) # Optional direct dependency of gdal only if lerc lib enabled
        # Drivers:
        if not (self.options.with_zlib and self.options.with_png and bool(self.options.with_jpeg)):
            # MRF raster driver always depends on zlib, libpng and libjpeg: https://github.com/OSGeo/gdal/issues/2581
            if tools.Version(self.version) < "3.0.0":
                args.append("--without-mrf")
            else:
                args.append("--disable-driver-mrf")
        args.append("--with-pg={}".format("yes" if self.options.with_pg else "no"))
        args.extend(["--without-grass", "--without-libgrass"]) # TODO: to implement when libgrass lib available
        args.append("--with-cfitsio={}".format(tools.unix_path(self.deps_cpp_info["cfitsio"].rootpath) if self.options.with_cfitsio else "no"))
        args.append("--with-pcraster={}".format("internal" if self.options.with_pcraster else "no")) # TODO: use conan recipe when available instead of internal one
        args.append("--with-png={}".format(tools.unix_path(self.deps_cpp_info["libpng"].rootpath) if self.options.with_png else "no"))
        args.append("--with-dds={}".format(tools.unix_path(self.deps_cpp_info["crunch"].rootpath) if self.options.with_dds else "no"))
        args.append("--with-gta={}".format(tools.unix_path(self.deps_cpp_info["libgta"].rootpath) if self.options.with_gta else "no"))
        args.append("--with-pcidsk={}".format("internal" if self.options.with_pcidsk else "no")) # TODO: use conan recipe when available instead of internal one
        args.append("--with-libtiff={}".format(tools.unix_path(self.deps_cpp_info["libtiff"].rootpath))) # always required !
        args.append("--with-geotiff={}".format(tools.unix_path(self.deps_cpp_info["libgeotiff"].rootpath))) # always required !
        if self.options.with_jpeg == "libjpeg":
            args.append("--with-jpeg={}".format(tools.unix_path(self.deps_cpp_info["libjpeg"].rootpath)))
        elif self.options.with_jpeg == "libjpeg-turbo":
            args.append("--with-jpeg={}".format(tools.unix_path(self.deps_cpp_info["libjpeg-turbo"].rootpath)))
        else:
            args.append("--without-jpeg")
        args.append("--without-jpeg12") # disabled: it requires internal libjpeg and libgeotiff
        args.append("--with-charls={}".format("yes" if self.options.with_charls else "no"))
        args.append("--with-gif={}".format(tools.unix_path(self.deps_cpp_info["giflib"].rootpath) if self.options.with_gif else "no"))
        args.append("--without-ogdi") # TODO: to implement when ogdi lib available (https://sourceforge.net/projects/ogdi/)
        args.append("--without-fme") # commercial library
        args.append("--without-sosi") # TODO: to implement when fyba lib available
        args.append("--without-mongocxx") # TODO: handle mongo-cxx-driver v2
        args.append("--with-mongocxxv3={}".format("yes" if self.options.with_mongocxx else "no"))
        args.append("--with-hdf4={}".format("yes" if self.options.with_hdf4 else "no"))
        args.append("--with-hdf5={}".format("yes" if self.options.with_hdf5 else "no"))
        args.append("--with-kea={}".format("yes" if self.options.with_kea else "no"))
        args.append("--with-netcdf={}".format(tools.unix_path(self.deps_cpp_info["netcdf"].rootpath) if self.options.with_netcdf else "no"))
        args.append("--with-jasper={}".format(tools.unix_path(self.deps_cpp_info["jasper"].rootpath) if self.options.with_jasper else "no"))
        args.append("--with-openjpeg={}".format("yes" if self.options.with_openjpeg else "no"))
        args.append("--without-fgdb") # TODO: to implement when file-geodatabase-api lib available
        args.append("--without-ecw") # commercial library
        args.append("--without-kakadu") # commercial library
        args.extend(["--without-mrsid", "--without-jp2mrsid", "--without-mrsid_lidar"]) # commercial library
        args.append("--without-jp2lura") # commercial library
        args.append("--without-msg") # commercial library
        args.append("--without-oci") # TODO
        args.append("--with-gnm={}".format("yes" if self.options.with_gnm else "no"))
        args.append("--with-mysql={}".format("yes" if bool(self.options.with_mysql) else "no"))
        args.append("--without-ingres") # commercial library
        args.append("--with-xerces={}".format(tools.unix_path(self.deps_cpp_info["xerces-c"].rootpath) if self.options.with_xerces else "no"))
        args.append("--with-expat={}".format("yes" if self.options.with_expat else "no"))
        args.append("--with-libkml={}".format(tools.unix_path(self.deps_cpp_info["libkml"].rootpath) if self.options.with_libkml else "no"))
        if self.options.with_odbc:
            args.append("--with-odbc={}".format("yes" if self.settings.os == "Windows" else tools.unix_path(self.deps_cpp_info["odbc"].rootpath)))
        else:
            args.append("--without-odbc")
        args.append("--without-dods-root") # TODO: to implement when libdap lib available
        args.append("--with-curl={}".format("yes" if self.options.with_curl else "no"))
        args.append("--with-xml2={}".format("yes" if self.options.with_xml2 else "no"))
        args.append("--without-spatialite") # TODO: to implement when libspatialite lib available
        args.append("--with-sqlite3={}".format("yes" if self.options.get_safe("with_sqlite3") else "no"))
        args.append("--without-rasterlite2") # TODO: to implement when rasterlite2 lib available
        args.append("--with-pcre={}".format("yes" if self.options.get_safe("with_pcre") else "no"))
        args.append("--without-teigha") # commercial library
        args.append("--without-idb") # commercial library
        if tools.Version(self.version) < "3.2.0":
            args.append("--without-sde") # commercial library
        args.append("--without-epsilon") # TODO: to implement when epsilon lib available
        args.append("--with-webp={}".format(tools.unix_path(self.deps_cpp_info["libwebp"].rootpath) if self.options.with_webp else "no"))
        args.append("--with-geos={}".format("yes" if self.options.with_geos else "no"))
        args.append("--without-sfcgal") # TODO: to implement when sfcgal lib available
        args.append("--with-qhull={}".format("yes" if self.options.with_qhull else "no"))
        if self.options.with_opencl:
            args.extend([
                "--with-opencl",
                "--with-opencl-include={}".format(tools.unix_path(self.deps_cpp_info["opencl-headers"].include_paths[0])),
                "--with-opencl-lib=-L{}".format(tools.unix_path(self.deps_cpp_info["opencl-icd-loader"].lib_paths[0]))
            ])
        else:
            args.append("--without-opencl")
        args.append("--with-freexl={}".format("yes" if self.options.with_freexl else "no"))
        args.append("--with-libjson-c={}".format(tools.unix_path(self.deps_cpp_info["json-c"].rootpath))) # always required !
        if self.options.without_pam:
            args.append("--without-pam")
        args.append("--with-poppler={}".format("yes" if self.options.with_poppler else "no"))
        if self.options.with_podofo:
            args.extend([
                "--with-podofo={}".format(tools.unix_path(self.deps_cpp_info["podofo"].rootpath)),
                "--with-podofo-lib=-l{}".format(" -l".join(self._gather_libs("podofo")))
            ])
        else:
            args.append("--without-podofo")
        args.append("--without-pdfium") # TODO: to implement when pdfium lib available
        args.append("--without-perl")
        args.append("--without-python")
        args.append("--without-java")
        args.append("--without-hdfs")
        if tools.Version(self.version) >= "3.0.0":
            args.append("--without-tiledb") # TODO: to implement when tiledb lib available
        args.append("--without-mdb")
        args.append("--without-rasdaman") # TODO: to implement when rasdaman lib available
        if tools.Version(self.version) >= "3.1.0":
            args.append("--without-rdb") # commercial library
        args.append("--without-armadillo") # TODO: to implement when armadillo lib available
        args.append("--with-cryptopp={}".format(tools.unix_path(self.deps_cpp_info["cryptopp"].rootpath) if self.options.with_cryptopp else "no"))
        args.append("--with-crypto={}".format("yes" if self.options.with_crypto else "no"))
        args.append("--with-lerc={}".format("no" if self.options.without_lerc else "yes"))
        if self.options.with_null:
            args.append("--with-null")
        if self._has_with_exr_option:
            args.append("--with-exr={}".format("yes" if self.options.with_exr else "no"))
        if self._has_with_heif_option:
            args.append("--with-heif={}".format("yes" if self.options.with_heif else "no"))

        # Inject -stdlib=libc++ for clang with libc++
        env_build_vars = self._autotools.vars
        if self.settings.compiler == "clang" and \
           self.settings.os == "Linux" and tools.stdcpp_library(self) == "c++":
            env_build_vars["LDFLAGS"] = "-stdlib=libc++ {}".format(env_build_vars["LDFLAGS"])

        self._autotools.configure(args=args, vars=env_build_vars)
        return self._autotools

    @contextmanager
    def _msvc_build_environment(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    yield

    @contextmanager
    def _autotools_build_environment(self):
        with tools.chdir(self._source_subfolder):
            with tools.run_environment(self):
                with tools.environment_append({"PKG_CONFIG_PATH": tools.unix_path(self.build_folder)}):
                    yield

    def build(self):
        self._validate_dependency_graph()
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._edit_nmake_opt()
            with self._msvc_build_environment():
                self.run("nmake -f makefile.vc {}".format(" ".join(self._get_nmake_args())))
        else:
            with self._autotools_build_environment():
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            with self._msvc_build_environment():
                self.run("nmake -f makefile.vc devinstall {}".format(" ".join(self._get_nmake_args())))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")
        else:
            with self._autotools_build_environment():
                autotools = self._configure_autotools()
                autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "gdalplugins"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.names["pkg_config"] = "gdal"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m"])
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi", "ws2_32"])
            if tools.Version(self.version) >= "3.2.0" and self.settings.compiler == "Visual Studio":
                self.cpp_info.system_libs.append("wbemuuid")
            if self.options.with_odbc and not self.options.shared:
                self.cpp_info.system_libs.extend(["odbc32", "odbccp32"])
                if self.settings.compiler == "Visual Studio":
                    self.cpp_info.system_libs.append("legacy_stdio_definitions")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))

        gdal_data_path = os.path.join(self.package_folder, "res", "gdal")
        self.output.info("Creating GDAL_DATA environment variable: {}".format(gdal_data_path))
        self.env_info.GDAL_DATA = gdal_data_path
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
