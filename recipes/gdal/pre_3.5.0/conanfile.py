from conan.tools.files import apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import functools
import os

required_conan_version = ">=1.45.0"


class GdalConan(ConanFile):
    name = "gdal"
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    topics = ("osgeo", "geospatial", "raster", "vector")
    homepage = "https://github.com/OSGeo/gdal"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd_intrinsics": [None, "sse", "ssse3", "avx"],
        "threadsafe": [True, False],
        "tools": [True, False],
        "with_zlib": [True, False],
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
        "with_zlib": True,
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

    generators = "pkg_config"

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

    @property
    def _has_with_blosc_option(self):
        return tools.Version(self.version) >= "3.4.0"

    @property
    def _has_with_lz4_option(self):
        return tools.Version(self.version) >= "3.4.0"

    @property
    def _has_with_brunsli_option(self):
        return tools.Version(self.version) >= "3.4.0"

    @property
    def _has_with_pcre2_option(self):
        return tools.Version(self.version) >= "3.4.1"

    @property
    def _has_reentrant_qhull_support(self):
        return tools.Version(self.version) >= "3.4.1"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        if not self._has_with_blosc_option:
            del self.options.with_blosc
        if not self._has_with_lz4_option:
            del self.options.with_lz4
        if not self._has_with_brunsli_option:
            del self.options.with_brunsli
        if not self._has_with_pcre2_option:
            del self.options.with_pcre2

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.simd_intrinsics
        if self.options.without_lerc:
            del self.options.with_zstd
        # if self.options.with_spatialite:
        #     del self.options.with_sqlite3
        if not self.options.get_safe("with_sqlite3", False):
            del self.options.with_pcre
            del self.options.with_pcre2
        if is_msvc(self):
            del self.options.threadsafe
            del self.options.with_null
            del self.options.with_zlib # zlib and png are always used in nmake build,
            del self.options.with_png  # and it's not trivial to fix
        self._strict_options_requirements()

    def _strict_options_requirements(self):
        if self.options.with_qhull:
            self.options["qhull"].reentrant = self._has_reentrant_qhull_support

    def requirements(self):
        self.requires("json-c/0.15")
        self.requires("libgeotiff/1.7.1")
        # self.requires("libopencad/0.0.2") # TODO: use conan recipe when available instead of internal one
        self.requires("libtiff/4.3.0")
        self.requires("proj/9.0.0")
        if tools.Version(self.version) >= "3.1.0":
            self.requires("flatbuffers/2.0.5")
        if self.options.get_safe("with_zlib", True):
            self.requires("zlib/1.2.12")
        if self.options.get_safe("with_libdeflate"):
            self.requires("libdeflate/1.12")
        if self.options.with_libiconv:
            self.requires("libiconv/1.16")
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
            self.requires("geos/3.10.2")
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            min_cppstd = 14 if self.options.with_charls else 11
            tools.check_min_cppstd(self, min_cppstd)
        if self.options.get_safe("with_pcre") and self.options.get_safe("with_pcre2"):
            raise ConanInvalidConfiguration("Enable either pcre or pcre2, not both")
        if self.options.get_safe("with_pcre2") and not self.options["pcre2"].build_pcre2_8:
            raise ConanInvalidConfiguration("gdal:with_pcre2=True requires pcre2:build_pcre2_8=True")
        if self.options.get_safe("with_brunsli"):
            raise ConanInvalidConfiguration("brunsli not available in conan-center yet")
        if self.options.get_safe("with_libdeflate") and not self.options.get_safe("with_zlib", True):
            raise ConanInvalidConfiguration("gdal:with_libdeflate=True requires gdal:with_zlib=True")
        if self.options.with_qhull:
            if self._has_reentrant_qhull_support and not self.options["qhull"].reentrant:
                raise ConanInvalidConfiguration("gdal {} depends on reentrant qhull.".format(self.version))
            elif not self._has_reentrant_qhull_support and self.options["qhull"].reentrant:
                raise ConanInvalidConfiguration("gdal {} depends on non-reentrant qhull.".format(self.version))
        if hasattr(self, "settings_build") and tools.cross_building(self):
            if self.options.shared:
                raise ConanInvalidConfiguration("GDAL build system can't cross-build shared lib")
            if self.options.tools:
                raise ConanInvalidConfiguration("GDAL build system can't cross-build tools")

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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if not is_msvc(self):
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

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
        if not is_msvc(self):
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

        # Disable tools
        if not self.options.tools:
            # autotools
            gnumakefile_apps = os.path.join(self._source_subfolder, "apps", "GNUmakefile")
            tools.replace_in_file(gnumakefile_apps,
                                  "default:	gdal-config-inst gdal-config $(BIN_LIST)",
                                  "default:	gdal-config-inst gdal-config")
            if tools.Version(self.version) < "3.4.0":
                clean_pattern = "$(RM) *.o $(BIN_LIST) core gdal-config gdal-config-inst"
            else:
                clean_pattern = "$(RM) *.o $(BIN_LIST) $(NON_DEFAULT_LIST) core gdal-config gdal-config-inst"
            tools.replace_in_file(gnumakefile_apps,
                                  clean_pattern,
                                  "$(RM) *.o core gdal-config gdal-config-inst")
            tools.replace_in_file(gnumakefile_apps,
                                  "for f in $(BIN_LIST) ; do $(INSTALL) $$f $(DESTDIR)$(INST_BIN) ; done",
                                  "")
            # msvc
            vcmakefile_apps = os.path.join(self._source_subfolder, "apps", "makefile.vc")
            tools.replace_in_file(vcmakefile_apps,
                                  "default:	",
                                  "default:	\n\nold-default:	")
            tools.replace_in_file(vcmakefile_apps,
                                  "copy *.exe $(BINDIR)",
                                  "")

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
            self._replace_in_nmake_opt("#CHARLS_LIB=e:\\work\\GIS\\gdal\\supportlibs\\charls\\bin\\Release\\x86\\CharLS.lib", "CHARLS_LIB=")
        # Inject required systems libs of dependencies
        self._replace_in_nmake_opt("ADD_LIBS	=", "ADD_LIBS={}".format(" ".join([lib + ".lib" for lib in self.deps_cpp_info.system_libs])))
        # Trick to enable OpenCL (option missing in upstream nmake files)
        if self.options.with_opencl:
            tools.replace_in_file(os.path.join(self._source_subfolder, "alg", "makefile.vc"),
                                  "$(GEOS_CFLAGS)", "$(GEOS_CFLAGS) /DHAVE_OPENCL")

    def _replace_in_nmake_opt(self, str1, str2):
        tools.replace_in_file(os.path.join(self.build_folder, self._source_subfolder, "nmake.opt"), str1, str2)

    @property
    def _nmake_args(self):
        rootpath = lambda req: self.deps_cpp_info[req].rootpath
        include_paths = lambda req: " -I".join(self.deps_cpp_info[req].include_paths)
        version = lambda req: tools.Version(self.deps_cpp_info[req].version)

        args = []
        args.append("GDAL_HOME=\"{}\"".format(self.package_folder))
        args.append("INCDIR=\"{}\"".format(os.path.join(self.package_folder, "include", "gdal")))
        args.append("DATADIR=\"{}\"".format(os.path.join(self.package_folder, "res", "gdal")))
        if self.settings.arch == "x86_64":
            args.append("WIN64=1")
        args.append("DEBUG={}".format("1" if self.settings.build_type == "Debug" else "0"))
        args.append("DLLBUILD={}".format("1" if self.options.shared else "0"))
        args.append("PROJ_INCLUDE=\"-I{}\"".format(include_paths("proj")))
        if self.options.with_libiconv:
            args.append("LIBICONV_INCLUDE=\"-I{}\"".format(include_paths("libiconv")))
            args.append("LIBICONV_CFLAGS=\"-DICONV_CONST=\"")
        args.append("JPEG_EXTERNAL_LIB=1")
        if self.options.with_jpeg == "libjpeg":
            args.append("JPEGDIR=\"{}\"".format(include_paths("libjpeg")))
        elif self.options.with_jpeg == "libjpeg-turbo":
            args.append("JPEGDIR=\"{}\"".format(include_paths("libjpeg-turbo")))
        args.append("PNG_EXTERNAL_LIB=1")
        args.append("PNGDIR=\"{}\"".format(include_paths("libpng")))
        if self.options.with_gif:
            args.append("GIF_SETTING=EXTERNAL")
        if self.options.with_pcraster:
            args.append("PCRASTER_SETTING=INTERNAL")
        args.append("TIFF_INC=\"-I{}\"".format(include_paths("libtiff")))
        args.append("GEOTIFF_INC=\"-I{}\"".format(include_paths("libgeotiff")))
        if self.options.with_libkml:
            args.append("LIBKML_DIR=\"{}\"".format(rootpath("libkml")))
        if self.options.with_expat:
            args.append("EXPAT_DIR=\"{}\"".format(rootpath("expat")))
            args.append("EXPAT_INCLUDE=\"-I{}\"".format(include_paths("expat")))
        if self.options.with_xerces:
            args.append("XERCES_DIR=\"{}\"".format(rootpath("xerces-c")))
            args.append("XERCES_INCLUDE=\"-I{}\"".format(include_paths("xerces-c")))
        if self.options.with_jasper:
            args.append("JASPER_DIR=\"{}\"".format(rootpath("jasper")))
        if self.options.with_hdf4:
            args.append("HDF4_DIR=\"{}\"".format(rootpath("hdf4")))
            args.append("HDF4_INCLUDE=\"{}\"".format(include_paths("hdf4")))
            if version("hdf4") >= "4.2.5":
                args.append("HDF4_HAS_MAXOPENFILES=YES")
        if self.options.with_hdf5:
            args.append("HDF5_DIR=\"{}\"".format(rootpath("hdf5")))
        if self.options.with_kea:
            args.append("KEA_CFLAGS=\"-I{}\"".format(include_paths("kealib")))
        if self.options.with_pg:
            args.append("PG_INC_DIR=\"{}\"".format(include_paths("libpq")))
        if self.options.with_mysql == "libmysqlclient":
            args.append("MYSQL_INC_DIR=\"{}\"".format(include_paths("libmysqlclient")))
        elif self.options.with_mysql == "mariadb-connector-c":
            args.append("MYSQL_INC_DIR=\"{}\"".format(include_paths("mariadb-connector-c")))
        if self.options.get_safe("with_sqlite3"):
            args.append("SQLITE_INC=\"-I{}\"".format(include_paths("sqlite3")))
        if self.options.get_safe("with_pcre2"):
            args.append("PCRE2_INC=\"-I{}\"".format(include_paths("pcre2")))
        if self.options.get_safe("with_pcre"):
            args.append("PCRE_INC=\"-I{}\"".format(include_paths("pcre")))
        if self.options.with_cfitsio:
            args.append("FITS_INC_DIR=\"{}\"".format(include_paths("cfitsio")))
        if self.options.with_netcdf:
            args.extend([
                "NETCDF_SETTING=YES",
                "NETCDF_INC_DIR=\"{}\"".format(include_paths("netcdf"))
            ])
            if self.options["netcdf"].netcdf4 and self.options["netcdf"].with_hdf5:
                args.append("NETCDF_HAS_NC4=YES")
            if tools.Version(self.version) >= "3.3.0" and \
               os.path.isfile(os.path.join(self.deps_cpp_info["netcdf"].rootpath, "include", "netcdf_mem.h")):
                args.append("NETCDF_HAS_NETCDF_MEM=YES")
        if self.options.with_curl:
            args.append("CURL_INC=\"-I{}\"".format(include_paths("libcurl")))
        if self.options.with_geos:
            args.append("GEOS_CFLAGS=\"-I{} -DHAVE_GEOS\"".format(include_paths("geos")))
        if self.options.with_openjpeg:
            args.append("OPENJPEG_ENABLED=YES")
        if self.options.get_safe("with_zlib", True):
            args.append("ZLIB_EXTERNAL_LIB=1")
            args.append("ZLIB_INC=\"-I{}\"".format(include_paths("zlib")))
        if self.options.get_safe("with_libdeflate"):
            args.append("LIBDEFLATE_CFLAGS=\"-I{}\"".format(include_paths("libdeflate")))
        if self.options.with_poppler:
            poppler_version = version("poppler")
            args.extend([
                "POPPLER_ENABLED=YES",
                "POPPLER_MAJOR_VERSION={}".format(poppler_version.major),
                "POPPLER_MINOR_VERSION={}".format(poppler_version.minor)
            ])
        if self.options.with_podofo:
            args.append("PODOFO_ENABLED=YES")
        if self.options.get_safe("with_zstd"):
            args.append("ZSTD_CFLAGS=\"-I{}\"".format(include_paths("zstd")))
        if self.options.get_safe("with_blosc"):
            args.append("BLOSC_CFLAGS=\"-I{}\"".format(include_paths("c-blosc")))
        if self.options.get_safe("with_lz4"):
            args.append("LZ4_CFLAGS=\"-I{}\"".format(include_paths("lz4")))
        if self.options.with_webp:
            args.append("WEBP_ENABLED=YES")
            args.append("WEBP_CFLAGS=\"-I{}\"".format(include_paths("libwebp")))
        if self.options.with_xml2:
            args.append("LIBXML2_INC=\"-I{}\"".format(include_paths("libxml2")))
        if self.options.with_gta:
            args.append("GTA_CFLAGS=\"-I{}\"".format(include_paths("libgta")))
        if self.options.with_mongocxx:
            args.append("MONGOCXXV3_CFLAGS=\"-I{}\"".format(include_paths("mongo-cxx-driver")))
        args.append("QHULL_SETTING={}".format("EXTERNAL" if self.options.with_qhull else "NO"))
        if self.options.with_qhull and self.options["qhull"].reentrant:
            args.append("QHULL_IS_LIBQHULL_R=1")
        if self.options.with_cryptopp:
            args.append("CRYPTOPP_INC=\"-I{}\"".format(include_paths("cryptopp")))
            if self.options["cryptopp"].shared:
                args.append("USE_ONLY_CRYPTODLL_ALG=YES")
        if self.options.with_crypto:
            args.append("OPENSSL_INC=\"-I{}\"".format(include_paths("openssl")))
        if self.options.without_lerc:
            args.append("HAVE_LERC=0")
        if self.options.get_safe("with_brunsli"):
            args.extend([
                "BRUNSLI_DIR=\"{}\"".format(rootpath("brunsli")),
                "BRUNSLI_INC=\"{}\"".format(include_paths("brunsli")),
            ])
        if self.options.with_charls:
            charls_version = version("charls")
            if charls_version >= "2.1.0":
                args.append("CHARLS_FLAGS=-DCHARLS_2_1")
            elif charls_version >= "2.0.0":
                args.append("CHARLS_FLAGS=-DCHARLS_2")
        if self.options.with_dds:
            args.append("CRUNCH_INC=\"-I{}\"".format(include_paths("crunch")))
        if self.options.get_safe("with_exr"):
            args.append("EXR_INC=\"-I{}\"".format(include_paths("openexr")))
        if self.options.get_safe("with_heif"):
            args.append("HEIF_INC=\"-I{}\"".format(include_paths("libheif")))

        return args

    def _gather_libs(self, p):
        libs = self.deps_cpp_info[p].libs + self.deps_cpp_info[p].system_libs
        for dep in self.deps_cpp_info[p].public_deps:
            for l in self._gather_libs(dep):
                if not l in libs:
                    libs.append(l)
        return libs

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        yes_no = lambda v: "yes" if v else "no"
        internal_no = lambda v: "internal" if v else "no"
        rootpath = lambda req: tools.unix_path(self.deps_cpp_info[req].rootpath)
        rootpath_no = lambda v, req: rootpath(req) if v else "no"

        args = []
        args.append("--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))))
        # Shared/Static
        args.extend([
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
        ])
        args.append("--includedir={}".format(tools.unix_path(os.path.join(self.package_folder, "include", "gdal"))))

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
        args.append("--with-threads={}".format(yes_no(self.options.threadsafe)))
        # Depencencies:
        args.append("--with-proj=yes") # always required !
        args.append("--with-libz={}".format(yes_no(self.options.with_zlib)))
        if self._has_with_libdeflate_option:
            args.append("--with-libdeflate={}".format(yes_no(self.options.with_libdeflate)))
        args.append("--with-libiconv-prefix={}".format(rootpath_no(self.options.with_libiconv, "libiconv")))
        args.append("--with-liblzma=no") # always disabled: liblzma is an optional transitive dependency of gdal (through libtiff).
        args.append("--with-zstd={}".format(yes_no(self.options.get_safe("with_zstd")))) # Optional direct dependency of gdal only if lerc lib enabled
        if self._has_with_blosc_option:
            args.append("--with-blosc={}".format(yes_no(self.options.with_blosc)))
        if self._has_with_lz4_option:
            args.append("--with-lz4={}".format(yes_no(self.options.with_lz4)))
        # Drivers:
        if not (self.options.with_zlib and self.options.with_png and bool(self.options.with_jpeg)):
            # MRF raster driver always depends on zlib, libpng and libjpeg: https://github.com/OSGeo/gdal/issues/2581
            if tools.Version(self.version) < "3.0.0":
                args.append("--without-mrf")
            else:
                args.append("--disable-driver-mrf")
        args.append("--with-pg={}".format(yes_no(self.options.with_pg)))
        args.extend(["--without-grass", "--without-libgrass"]) # TODO: to implement when libgrass lib available
        args.append("--with-cfitsio={}".format(rootpath_no(self.options.with_cfitsio, "cfitsio")))
        args.append("--with-pcraster={}".format(internal_no(self.options.with_pcraster))) # TODO: use conan recipe when available instead of internal one
        args.append("--with-png={}".format(rootpath_no(self.options.with_png, "libpng")))
        args.append("--with-dds={}".format(rootpath_no(self.options.with_dds, "crunch")))
        args.append("--with-gta={}".format(rootpath_no(self.options.with_gta, "libgta")))
        args.append("--with-pcidsk={}".format(internal_no(self.options.with_pcidsk))) # TODO: use conan recipe when available instead of internal one
        args.append("--with-libtiff={}".format(rootpath("libtiff"))) # always required !
        args.append("--with-geotiff={}".format(rootpath("libgeotiff"))) # always required !
        if self.options.with_jpeg == "libjpeg":
            args.append("--with-jpeg={}".format(rootpath("libjpeg")))
        elif self.options.with_jpeg == "libjpeg-turbo":
            args.append("--with-jpeg={}".format(rootpath("libjpeg-turbo")))
        else:
            args.append("--without-jpeg")
        args.append("--without-jpeg12") # disabled: it requires internal libjpeg and libgeotiff
        args.append("--with-charls={}".format(yes_no(self.options.with_charls)))
        args.append("--with-gif={}".format(rootpath_no(self.options.with_gif, "giflib")))
        args.append("--without-ogdi") # TODO: to implement when ogdi lib available (https://sourceforge.net/projects/ogdi/)
        args.append("--without-fme") # commercial library
        args.append("--without-sosi") # TODO: to implement when fyba lib available
        args.append("--without-mongocxx") # TODO: handle mongo-cxx-driver v2
        args.append("--with-mongocxxv3={}".format(yes_no(self.options.with_mongocxx)))
        args.append("--with-hdf4={}".format(yes_no(self.options.with_hdf4)))
        args.append("--with-hdf5={}".format(yes_no(self.options.with_hdf5)))
        args.append("--with-kea={}".format(yes_no(self.options.with_kea)))
        args.append("--with-netcdf={}".format(rootpath_no(self.options.with_netcdf, "netcdf")))
        args.append("--with-jasper={}".format(rootpath_no(self.options.with_jasper, "jasper")))
        args.append("--with-openjpeg={}".format(yes_no(self.options.with_openjpeg)))
        args.append("--without-fgdb") # TODO: to implement when file-geodatabase-api lib available
        args.append("--without-ecw") # commercial library
        args.append("--without-kakadu") # commercial library
        args.extend(["--without-mrsid", "--without-jp2mrsid", "--without-mrsid_lidar"]) # commercial library
        args.append("--without-jp2lura") # commercial library
        args.append("--without-msg") # commercial library
        args.append("--without-oci") # TODO
        args.append("--with-gnm={}".format(yes_no(self.options.with_gnm)))
        args.append("--with-mysql={}".format(yes_no(self.options.with_mysql)))
        args.append("--without-ingres") # commercial library
        args.append("--with-xerces={}".format(rootpath_no(self.options.with_xerces, "xerces-c")))
        args.append("--with-expat={}".format(yes_no(self.options.with_expat)))
        args.append("--with-libkml={}".format(rootpath_no(self.options.with_libkml, "libkml")))
        if self.options.with_odbc:
            args.append("--with-odbc={}".format("yes" if self.settings.os == "Windows" else rootpath("odbc")))
        else:
            args.append("--without-odbc")
        args.append("--without-dods-root") # TODO: to implement when libdap lib available
        args.append("--with-curl={}".format(yes_no(self.options.with_curl)))
        args.append("--with-xml2={}".format(yes_no(self.options.with_xml2)))
        args.append("--without-spatialite") # TODO: to implement when libspatialite lib available
        args.append("--with-sqlite3={}".format(yes_no(self.options.get_safe("with_sqlite3"))))
        args.append("--without-rasterlite2") # TODO: to implement when rasterlite2 lib available
        if self._has_with_pcre2_option:
            args.append("--with-pcre2={}".format(yes_no(self.options.get_safe("with_pcre2"))))
        args.append("--with-pcre={}".format(yes_no(self.options.get_safe("with_pcre"))))
        args.append("--without-teigha") # commercial library
        args.append("--without-idb") # commercial library
        if tools.Version(self.version) < "3.2.0":
            args.append("--without-sde") # commercial library
        if tools.Version(self.version) < "3.3.0":
            args.append("--without-epsilon")
        args.append("--with-webp={}".format(rootpath_no(self.options.with_webp, "libwebp")))
        args.append("--with-geos={}".format(yes_no(self.options.with_geos)))
        args.append("--without-sfcgal") # TODO: to implement when sfcgal lib available
        args.append("--with-qhull={}".format(yes_no(self.options.with_qhull)))
        if self.options.with_opencl:
            args.extend([
                "--with-opencl",
                "--with-opencl-include={}".format(tools.unix_path(self.deps_cpp_info["opencl-headers"].include_paths[0])),
                "--with-opencl-lib=-L{}".format(tools.unix_path(self.deps_cpp_info["opencl-icd-loader"].lib_paths[0]))
            ])
        else:
            args.append("--without-opencl")
        args.append("--with-freexl={}".format(yes_no(self.options.with_freexl)))
        args.append("--with-libjson-c={}".format(rootpath("json-c"))) # always required !
        if self.options.without_pam:
            args.append("--without-pam")
        args.append("--with-poppler={}".format(yes_no(self.options.with_poppler)))
        args.append("--with-podofo={}".format(rootpath_no(self.options.with_podofo, "podofo")))
        if self.options.with_podofo:
            args.append("--with-podofo-lib=-l{}".format(" -l".join(self._gather_libs("podofo"))))
        args.append("--without-pdfium") # TODO: to implement when pdfium lib available
        args.append("--without-perl")
        args.append("--without-python")
        args.append("--without-java")
        args.append("--without-hdfs")
        if tools.Version(self.version) >= "3.0.0":
            args.append("--without-tiledb") # TODO: to implement when tiledb lib available
        args.append("--without-mdb")
        args.append("--without-rasdaman") # TODO: to implement when rasdaman lib available
        if self._has_with_brunsli_option:
            args.append("--with-brunsli={}".format(yes_no(self.options.with_brunsli)))
        if tools.Version(self.version) >= "3.1.0":
            args.append("--without-rdb") # commercial library
        args.append("--without-armadillo") # TODO: to implement when armadillo lib available
        args.append("--with-cryptopp={}".format(rootpath_no(self.options.with_cryptopp, "cryptopp")))
        args.append("--with-crypto={}".format(yes_no(self.options.with_crypto)))
        if tools.Version(self.version) >= "3.3.0":
            args.append("--with-lerc={}".format(internal_no(not self.options.without_lerc)))
        else:
            args.append("--with-lerc={}".format(yes_no(not self.options.without_lerc)))
        if self.options.with_null:
            args.append("--with-null")
        if self._has_with_exr_option:
            args.append("--with-exr={}".format(yes_no(self.options.with_exr)))
        if self._has_with_heif_option:
            args.append("--with-heif={}".format(yes_no(self.options.with_heif)))

        # Inject -stdlib=libc++ for clang with libc++
        env_build_vars = autotools.vars
        if self.settings.compiler == "clang" and \
           self.settings.os == "Linux" and tools.stdcpp_library(self) == "c++":
            env_build_vars["LDFLAGS"] = "-stdlib=libc++ {}".format(env_build_vars["LDFLAGS"])

        autotools.configure(args=args, vars=env_build_vars)
        return autotools

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
        if is_msvc(self):
            self._edit_nmake_opt()
            with self._msvc_build_environment():
                self.run("nmake -f makefile.vc {}".format(" ".join(self._nmake_args)))
        else:
            with self._autotools_build_environment():
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
                # Required for cross-build to iOS, see https://github.com/OSGeo/gdal/issues/4123
                tools.replace_in_file(os.path.join("port", "cpl_config.h.in"),
                                      "/* port/cpl_config.h.in",
                                      "#pragma once\n/* port/cpl_config.h.in")
                # Relocatable shared lib on macOS
                tools.replace_in_file("configure",
                                      "-install_name \\$rpath/",
                                      "-install_name @rpath/")
                # avoid SIP issues on macOS when dependencies are shared
                if tools.is_apple_os(self.settings.os):
                    libpaths = ":".join(self.deps_cpp_info.lib_paths)
                    tools.replace_in_file(
                        "configure",
                        "#! /bin/sh\n",
                        "#! /bin/sh\nexport DYLD_LIBRARY_PATH={}:$DYLD_LIBRARY_PATH\n".format(libpaths),
                    )
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        if is_msvc(self):
            with self._msvc_build_environment():
                self.run("nmake -f makefile.vc devinstall {}".format(" ".join(self._nmake_args)))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")
        else:
            with self._autotools_build_environment():
                autotools = self._configure_autotools()
                autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "gdalplugins"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GDAL")
        self.cpp_info.set_property("cmake_target_name", "GDAL::GDAL")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "gdal")

        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package"] = "GDAL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "GDAL"
        self.cpp_info.includedirs.append(os.path.join("include", "gdal"))

        lib_suffix = ""
        if is_msvc(self):
            if self.options.shared:
                lib_suffix += "_i"
            if self.settings.build_type == "Debug":
                lib_suffix += "_d"
        self.cpp_info.libs = ["gdal{}".format(lib_suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi", "ws2_32"])
            if tools.Version(self.version) >= "3.2.0" and is_msvc(self):
                self.cpp_info.system_libs.append("wbemuuid")
            if self.options.with_odbc and not self.options.shared:
                self.cpp_info.system_libs.extend(["odbc32", "odbccp32"])
                if is_msvc(self):
                    self.cpp_info.system_libs.append("legacy_stdio_definitions")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))

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
