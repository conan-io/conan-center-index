from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building, stdcpp_library, valid_min_cppstd
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeDeps, NMakeToolchain, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.58.0"


class GdalConan(ConanFile):
    name = "gdal"
    description = "GDAL is an open source X/MIT licensed translator library " \
                  "for raster and vector geospatial data formats."
    license = "MIT"
    topics = ("osgeo", "geospatial", "raster", "vector")
    homepage = "https://github.com/OSGeo/gdal"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
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
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo", "mozjpeg"],
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)


    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.arch not in ["x86", "x86_64"]:
            self.options.rm_safe("simd_intrinsics")
        if self.options.without_lerc:
            self.options.rm_safe("with_zstd")
        # if self.options.with_spatialite:
        #     self.options.rm_safe("with_sqlite3
        if not self.options.get_safe("with_sqlite3"):
            self.options.rm_safe("with_pcre")
            self.options.rm_safe("with_pcre2")
        if is_msvc(self):
            self.options.rm_safe("threadsafe")
            self.options.rm_safe("with_null")
            self.options.rm_safe("with_zlib") # zlib and png are always used in nmake build,
            self.options.rm_safe("with_png")  # and it's not trivial to fix

        if self.options.with_qhull:
            self.options["qhull"].reentrant = True

    def layout(self):
        basic_layout(self, src_folder="src")
        self.folders.build = self.folders.source

    def requirements(self):
        self.requires("json-c/0.17")
        self.requires("libgeotiff/1.7.1")
        # self.requires("libopencad/0.0.2") # TODO: use conan recipe when available instead of internal one
        self.requires("libtiff/4.6.0")
        self.requires("proj/9.3.1")
        self.requires("flatbuffers/2.0.5")
        if self.options.get_safe("with_zlib", True):
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_libdeflate:
            self.requires("libdeflate/1.19")
        if self.options.with_libiconv:
            self.requires("libiconv/1.17")
        if self.options.get_safe("with_zstd"):
            self.requires("zstd/1.5.5")
        if self.options.with_blosc:
            self.requires("c-blosc/1.21.3")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_pg:
            self.requires("libpq/15.4")
        # if self.options.with_libgrass:
        #     self.requires("libgrass/x.x.x")
        if self.options.with_cfitsio:
            self.requires("cfitsio/4.1.0")
        # if self.options.with_pcraster:
        #     self.requires("pcraster-rasterformat/1.3.2")
        if self.options.get_safe("with_png", True):
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_dds:
            self.requires("crunch/cci.20190615")
        if self.options.with_gta:
            self.requires("libgta/1.2.1")
        # if self.options.with_pcidsk:
        #     self.requires("pcidsk/x.x.x")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.1")
        if self.options.with_charls:
            self.requires("charls/2.4.1")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        # if self.options.with_ogdi:
        #     self.requires("ogdi/4.1.0")
        # if self.options.with_sosi:
        #     self.requires("fyba/4.1.1")
        if self.options.with_mongocxx:
            self.requires("mongo-cxx-driver/3.6.7")
        if self.options.with_hdf4:
            self.requires("hdf4/4.2.15")
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.0")
        if self.options.with_kea:
            self.requires("kealib/1.4.14")
        if self.options.with_netcdf:
            self.requires("netcdf/4.8.1")
        if self.options.with_jasper:
            self.requires("jasper/4.0.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        # if self.options.with_fgdb:
        #     self.requires("file-geodatabase-api/x.x.x")
        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.0.31")
        elif self.options.with_mysql == "mariadb-connector-c":
            self.requires("mariadb-connector-c/3.1.12")
        if self.options.with_xerces:
            self.requires("xerces-c/3.2.4")
        if self.options.with_expat:
            self.requires("expat/[>=2.6.2 <3]")
        if self.options.with_libkml:
            self.requires("libkml/1.3.0")
        if self.options.with_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.11")
        # if self.options.with_dods_root:
        #     self.requires("libdap/3.20.6")
        if self.options.with_curl:
            self.requires("libcurl/[>=8.2 <9]")
        if self.options.with_xml2:
            self.requires("libxml2/2.10.3")
        # if self.options.with_spatialite:
        #     self.requires("libspatialite/4.3.0a")
        if self.options.get_safe("with_sqlite3"):
            self.requires("sqlite3/3.44.2")
        # if self.options.with_rasterlite2:
        #     self.requires("rasterlite2/x.x.x")
        if self.options.get_safe("with_pcre"):
            self.requires("pcre/8.45")
        if self.options.get_safe("with_pcre2"):
            self.requires("pcre2/10.42")
        if self.options.with_webp:
            self.requires("libwebp/1.3.1")
        if self.options.with_geos:
            self.requires("geos/3.11.1")
        # if self.options.with_sfcgal:
        #     self.requires("sfcgal/1.3.7")
        if self.options.with_qhull:
            self.requires("qhull/8.0.1")
        if self.options.with_opencl:
            self.requires("opencl-headers/2022.09.30")
            self.requires("opencl-icd-loader/2022.09.30")
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
            self.requires("cryptopp/8.7.0")
        if self.options.with_crypto:
            self.requires("openssl/[>=1.1 <4]")
        # if not self.options.without_lerc:
        #     self.requires("lerc/2.1") # TODO: use conan recipe (not possible yet because lerc API is broken for GDAL)
        if self.options.with_exr:
            self.requires("openexr/3.1.9")
        if self.options.with_heif:
            self.requires("libheif/1.13.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            min_cppstd = 14 if self.options.with_charls else 11
            check_min_cppstd(self, min_cppstd)
        if self.options.get_safe("with_pcre") and self.options.get_safe("with_pcre2"):
            raise ConanInvalidConfiguration("Enable either pcre or pcre2, not both")
        if self.options.get_safe("with_pcre2") and not self.dependencies["pcre2"].options.build_pcre2_8:
            raise ConanInvalidConfiguration("gdal:with_pcre2=True requires pcre2:build_pcre2_8=True")
        if self.options.with_brunsli:
            raise ConanInvalidConfiguration("brunsli not available in conan-center yet")
        if self.options.with_libdeflate and not self.options.get_safe("with_zlib", True):
            raise ConanInvalidConfiguration("gdal:with_libdeflate=True requires gdal:with_zlib=True")
        if self.options.with_qhull:
            if not self.dependencies["qhull"].options.reentrant:
                raise ConanInvalidConfiguration(f"{self.ref} depends on reentrant qhull.")
        if hasattr(self, "settings_build") and cross_building(self):
            if self.options.shared:
                raise ConanInvalidConfiguration(f"{self.ref} can't cross-build shared lib")
            if self.options.tools:
                raise ConanInvalidConfiguration(f"{self.ref} can't cross-build tools")

        if Version(self.dependencies["libtiff"].ref.version) < "4.0.0":
            raise ConanInvalidConfiguration(f"{self.ref} requires libtiff >= 4.0.0")
        if self.options.with_mongocxx:
            mongocxx_version = Version(self.dependencies["mongo-cxx-driver"].ref.version)
            if mongocxx_version < "3.0.0":
                # TODO: handle mongo-cxx-driver v2
                raise ConanInvalidConfiguration(f"{self.ref} with mongo-cxx-driver < 3.0.0 not yet supported in this recipe.")
            if mongocxx_version < "3.4.0":
                raise ConanInvalidConfiguration(f"{self.ref} with mongo-cxx-driver v3 requires 3.4.0 at least.")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.1.0")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
            os.path.join("ogr", "ogrsf_frmts", "flatgeobuf", "flatbuffers"),
        ]
        for lib_subdir in embedded_libs:
            rmdir(self, os.path.join(self.source_folder, lib_subdir))

        # OpenCL headers
        replace_in_file(self, os.path.join(self.source_folder, "alg", "gdalwarpkernel_opencl.h"),
                              "#include <OpenCL/OpenCL.h>",
                              "#include <CL/opencl.h>")

        # More patches for autotools build
        if not is_msvc(self):
            configure_ac = os.path.join(self.source_folder, "configure.ac")
            # Workaround for nc-config not packaged in netcdf recipe (gdal relies on it to check nc4 and hdf4 support in netcdf):
            if self.options.with_netcdf:
                if self.dependencies["netcdf"].options.netcdf4 and self.dependencies["netcdf"].options.with_hdf5:
                    replace_in_file(self, configure_ac, "NETCDF_HAS_NC4=no", "NETCDF_HAS_NC4=yes")
            # Fix zlib checks and -lz injection to ensure to use external zlib and not fail others checks
            if self.options.get_safe("with_zlib", True):
                zlib_name = self.dependencies["zlib"].cpp_info.aggregated_components().libs[0]
                replace_in_file(self, configure_ac, "AC_CHECK_LIB(z,", f"AC_CHECK_LIB({zlib_name},")
                replace_in_file(self, configure_ac, "-lz ", f"-l{zlib_name} ")
            # Workaround for autoconf 2.71
            with open(os.path.join(self.source_folder, "config.rpath"), "w"):
                pass

        # Disable tools
        if not self.options.tools:
            # autotools
            gnumakefile_apps = os.path.join(self.source_folder, "apps", "GNUmakefile")
            replace_in_file(self, gnumakefile_apps,
                                  "default:	gdal-config-inst gdal-config $(BIN_LIST)",
                                  "default:	gdal-config-inst gdal-config")
            replace_in_file(self, gnumakefile_apps,
                                  "$(RM) *.o $(BIN_LIST) $(NON_DEFAULT_LIST) core gdal-config gdal-config-inst",
                                  "$(RM) *.o core gdal-config gdal-config-inst")
            replace_in_file(self, gnumakefile_apps,
                                  "for f in $(BIN_LIST) ; do $(INSTALL) $$f $(DESTDIR)$(INST_BIN) ; done",
                                  "")
            # msvc
            vcmakefile_apps = os.path.join(self.source_folder, "apps", "makefile.vc")
            replace_in_file(self, vcmakefile_apps, "default:	", "default:	\n\nold-default:	")
            replace_in_file(self, vcmakefile_apps, "copy *.exe $(BINDIR)", "")

    def _build_nmake(self):
        def replace_in_nmake_opt(str1, str2):
            replace_in_file(self, os.path.join(self.source_folder, "nmake.opt"), str1, str2)

        simd_intrinsics = str(self.options.get_safe("simd_intrinsics", False))
        if simd_intrinsics != "avx":
            replace_in_nmake_opt("AVXFLAGS = /DHAVE_AVX_AT_COMPILE_TIME", "")
        if simd_intrinsics not in ["sse3", "avx"]:
            replace_in_nmake_opt("SSSE3FLAGS = /DHAVE_SSSE3_AT_COMPILE_TIME", "")
        if simd_intrinsics not in ["sse", "sse3", "avx"]:
            replace_in_nmake_opt("SSEFLAGS = /DHAVE_SSE_AT_COMPILE_TIME", "")
        if self.options.without_pam:
            replace_in_nmake_opt("PAM_SETTING=-DPAM_ENABLED", "")
        if not self.options.with_gnm:
            replace_in_nmake_opt("INCLUDE_GNM_FRMTS = YES", "")
        if not self.options.with_odbc:
            replace_in_nmake_opt("ODBC_SUPPORTED = 1", "")
        if not bool(self.options.with_jpeg):
            replace_in_nmake_opt("JPEG_SUPPORTED = 1", "")
        replace_in_nmake_opt("JPEG12_SUPPORTED = 1", "")
        if not self.options.with_pcidsk:
            replace_in_nmake_opt("PCIDSK_SETTING=INTERNAL", "")
        if self.options.with_pg:
            replace_in_nmake_opt("#PG_LIB = n:\\pkg\\libpq_win32\\lib\\libpqdll.lib wsock32.lib", "PG_LIB=")
        if bool(self.options.with_mysql):
            replace_in_nmake_opt("#MYSQL_LIB = D:\\Software\\MySQLServer4.1\\lib\\opt\\libmysql.lib advapi32.lib", "MYSQL_LIB=")
        if self.options.get_safe("with_sqlite3"):
            replace_in_nmake_opt("#SQLITE_LIB=N:\\pkg\\sqlite-win32\\sqlite3_i.lib", "SQLITE_LIB=")
        if self.options.with_curl:
            replace_in_nmake_opt("#CURL_LIB = $(CURL_DIR)/libcurl.lib wsock32.lib wldap32.lib winmm.lib", "CURL_LIB=")
        if self.options.with_freexl:
            replace_in_nmake_opt("#FREEXL_LIBS = e:/freexl-1.0.0a/freexl_i.lib", "FREEXL_LIBS=")
        if not (self.options.get_safe("with_zlib", True) and self.options.get_safe("with_png", True) and bool(self.options.with_jpeg)):
            replace_in_nmake_opt("MRF_SETTING=yes", "")
        if self.options.with_charls:
            replace_in_nmake_opt("#CHARLS_LIB=e:\\work\\GIS\\gdal\\supportlibs\\charls\\bin\\Release\\x86\\CharLS.lib", "CHARLS_LIB=")
        # Trick to enable OpenCL (option missing in upstream nmake files)
        if self.options.with_opencl:
            replace_in_file(self, os.path.join(self.source_folder, "alg", "makefile.vc"),
                                  "$(GEOS_CFLAGS)", "$(GEOS_CFLAGS) /DHAVE_OPENCL")

        with chdir(self, self.source_folder):
            self.run(f"nmake -f makefile.vc {' '.join(self._nmake_args)}")

    @property
    def _nmake_args(self):
        rootpath = lambda req: self.dependencies[req].package_folder
        include_paths = lambda req: " -I".join(self.dependencies[req].cpp_info.aggregated_components().includedirs)
        version = lambda req: Version(self.dependencies[req].ref.version)

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
        elif self.options.with_jpeg == "mozjpeg":
            args.append("JPEGDIR=\"{}\"".format(include_paths("mozjpeg")))
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
            if self.dependencies["netcdf"].options.netcdf4 and self.dependencies["netcdf"].options.with_hdf5:
                args.append("NETCDF_HAS_NC4=YES")
            if os.path.isfile(os.path.join(rootpath("netcdf"), "include", "netcdf_mem.h")):
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
        if self.options.with_libdeflate:
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
        if self.options.with_blosc:
            args.append("BLOSC_CFLAGS=\"-I{}\"".format(include_paths("c-blosc")))
        if self.options.with_lz4:
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
        if self.options.with_qhull and self.dependencies["qhull"].options.reentrant:
            args.append("QHULL_IS_LIBQHULL_R=1")
        if self.options.with_cryptopp:
            args.append("CRYPTOPP_INC=\"-I{}\"".format(include_paths("cryptopp")))
            if self.dependencies["cryptopp"].options.shared:
                args.append("USE_ONLY_CRYPTODLL_ALG=YES")
        if self.options.with_crypto:
            args.append("OPENSSL_INC=\"-I{}\"".format(include_paths("openssl")))
        if self.options.without_lerc:
            args.append("HAVE_LERC=0")
        if self.options.with_brunsli:
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
        if self.options.with_exr:
            args.append("EXR_INC=\"-I{}\"".format(include_paths("openexr")))
        if self.options.with_heif:
            args.append("HEIF_INC=\"-I{}\"".format(include_paths("libheif")))

        return args

    def _gather_libs(self, p):
        deps_cpp_info = self.dependencies[p].cpp_info.aggregated_components()
        libs = deps_cpp_info.libs + deps_cpp_info.system_libs
        for dep in self.dependencies[p].dependencies:
            for l in self._gather_libs(dep):
                if not l in libs:
                    libs.append(l)
        return libs

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            deps = NMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)

            yes_no = lambda v: "yes" if v else "no"
            internal_no = lambda v: "internal" if v else "no"
            rootpath = lambda req: unix_path(self, self.dependencies[req].package_folder)
            rootpath_no = lambda v, req: rootpath(req) if v else "no"

            tc.configure_args.extend([
                "--includedir=${prefix}/include/gdal",
                "--datarootdir=${prefix}/res",
            ])

            # Enable C++14 if requested in conan profile or if with_charls enabled
            if (self.settings.compiler.get_safe("cppstd") and valid_min_cppstd(self, 14)) or self.options.with_charls:
                tc.configure_args.append("--with-cpp14")
            # Debug
            if self.settings.build_type == "Debug":
                tc.configure_args.append("--enable-debug")
            # SIMD Intrinsics
            simd_intrinsics = self.options.get_safe("simd_intrinsics", False)
            if not simd_intrinsics:
                tc.configure_args.extend(["--without-sse", "--without-ssse3", "--without-avx"])
            elif simd_intrinsics == "sse":
                tc.configure_args.extend(["--with-sse", "--without-ssse3", "--without-avx"])
            elif simd_intrinsics == "ssse3":
                tc.configure_args.extend(["--with-sse", "--with-ssse3", "--without-avx"])
            elif simd_intrinsics == "avx":
                tc.configure_args.extend(["--with-sse", "--with-ssse3", "--with-avx"])
            # LTO (disabled)
            tc.configure_args.append("--disable-lto")
            # Symbols
            tc.configure_args.append("--with-hide_internal_symbols")
            # Do not add /usr/local/lib and /usr/local/include
            tc.configure_args.append("--without-local")
            # Threadsafe
            tc.configure_args.append("--with-threads={}".format(yes_no(self.options.threadsafe)))
            # Depencencies:
            tc.configure_args.append("--with-proj=yes") # always required !
            tc.configure_args.append("--with-libz={}".format(yes_no(self.options.with_zlib)))
            tc.configure_args.append("--with-libdeflate={}".format(yes_no(self.options.with_libdeflate)))
            tc.configure_args.append("--with-libiconv-prefix={}".format(rootpath_no(self.options.with_libiconv, "libiconv")))
            tc.configure_args.append("--with-liblzma=no") # always disabled: liblzma is an optional transitive dependency of gdal (through libtiff).
            tc.configure_args.append("--with-zstd={}".format(yes_no(self.options.get_safe("with_zstd")))) # Optional direct dependency of gdal only if lerc lib enabled
            tc.configure_args.append("--with-blosc={}".format(yes_no(self.options.with_blosc)))
            tc.configure_args.append("--with-lz4={}".format(yes_no(self.options.with_lz4)))
            # Drivers:
            if not (self.options.with_zlib and self.options.with_png and bool(self.options.with_jpeg)):
                # MRF raster driver always depends on zlib, libpng and libjpeg: https://github.com/OSGeo/gdal/issues/2581
                tc.configure_args.append("--disable-driver-mrf")
            tc.configure_args.append("--with-pg={}".format(yes_no(self.options.with_pg)))
            tc.configure_args.extend(["--without-grass", "--without-libgrass"]) # TODO: to implement when libgrass lib available
            tc.configure_args.append("--with-cfitsio={}".format(rootpath_no(self.options.with_cfitsio, "cfitsio")))
            tc.configure_args.append("--with-pcraster={}".format(internal_no(self.options.with_pcraster))) # TODO: use conan recipe when available instead of internal one
            tc.configure_args.append("--with-png={}".format(rootpath_no(self.options.with_png, "libpng")))
            tc.configure_args.append("--with-dds={}".format(rootpath_no(self.options.with_dds, "crunch")))
            tc.configure_args.append("--with-gta={}".format(rootpath_no(self.options.with_gta, "libgta")))
            tc.configure_args.append("--with-pcidsk={}".format(internal_no(self.options.with_pcidsk))) # TODO: use conan recipe when available instead of internal one
            tc.configure_args.append("--with-libtiff={}".format(rootpath("libtiff"))) # always required !
            tc.configure_args.append("--with-geotiff={}".format(rootpath("libgeotiff"))) # always required !
            if self.options.with_jpeg == "libjpeg":
                tc.configure_args.append("--with-jpeg={}".format(rootpath("libjpeg")))
            elif self.options.with_jpeg == "libjpeg-turbo":
                tc.configure_args.append("--with-jpeg={}".format(rootpath("libjpeg-turbo")))
            elif self.options.with_jpeg == "mozjpeg":
                tc.configure_args.append("--with-jpeg={}".format(rootpath("mozjpeg")))
            else:
                tc.configure_args.append("--without-jpeg")
            tc.configure_args.append("--without-jpeg12") # disabled: it requires internal libjpeg and libgeotiff
            tc.configure_args.append("--with-charls={}".format(yes_no(self.options.with_charls)))
            tc.configure_args.append("--with-gif={}".format(rootpath_no(self.options.with_gif, "giflib")))
            tc.configure_args.append("--without-ogdi") # TODO: to implement when ogdi lib available (https://sourceforge.net/projects/ogdi/)
            tc.configure_args.append("--without-fme") # commercial library
            tc.configure_args.append("--without-sosi") # TODO: to implement when fyba lib available
            tc.configure_args.append("--without-mongocxx") # TODO: handle mongo-cxx-driver v2
            tc.configure_args.append("--with-mongocxxv3={}".format(yes_no(self.options.with_mongocxx)))
            tc.configure_args.append("--with-hdf4={}".format(yes_no(self.options.with_hdf4)))
            tc.configure_args.append("--with-hdf5={}".format(yes_no(self.options.with_hdf5)))
            tc.configure_args.append("--with-kea={}".format(yes_no(self.options.with_kea)))
            tc.configure_args.append("--with-netcdf={}".format(rootpath_no(self.options.with_netcdf, "netcdf")))
            tc.configure_args.append("--with-jasper={}".format(rootpath_no(self.options.with_jasper, "jasper")))
            tc.configure_args.append("--with-openjpeg={}".format(yes_no(self.options.with_openjpeg)))
            tc.configure_args.append("--without-fgdb") # TODO: to implement when file-geodatabase-api lib available
            tc.configure_args.append("--without-ecw") # commercial library
            tc.configure_args.append("--without-kakadu") # commercial library
            tc.configure_args.extend(["--without-mrsid", "--without-jp2mrsid", "--without-mrsid_lidar"]) # commercial library
            tc.configure_args.append("--without-jp2lura") # commercial library
            tc.configure_args.append("--without-msg") # commercial library
            tc.configure_args.append("--without-oci") # TODO
            tc.configure_args.append("--with-gnm={}".format(yes_no(self.options.with_gnm)))
            tc.configure_args.append("--with-mysql={}".format(yes_no(self.options.with_mysql)))
            tc.configure_args.append("--without-ingres") # commercial library
            tc.configure_args.append("--with-xerces={}".format(rootpath_no(self.options.with_xerces, "xerces-c")))
            tc.configure_args.append("--with-expat={}".format(yes_no(self.options.with_expat)))
            tc.configure_args.append("--with-libkml={}".format(rootpath_no(self.options.with_libkml, "libkml")))
            if self.options.with_odbc:
                tc.configure_args.append("--with-odbc={}".format("yes" if self.settings.os == "Windows" else rootpath("odbc")))
            else:
                tc.configure_args.append("--without-odbc")
            tc.configure_args.append("--without-dods-root") # TODO: to implement when libdap lib available
            tc.configure_args.append("--with-curl={}".format(yes_no(self.options.with_curl)))
            tc.configure_args.append("--with-xml2={}".format(yes_no(self.options.with_xml2)))
            tc.configure_args.append("--without-spatialite") # TODO: to implement when libspatialite lib available
            tc.configure_args.append("--with-sqlite3={}".format(yes_no(self.options.get_safe("with_sqlite3"))))
            tc.configure_args.append("--without-rasterlite2") # TODO: to implement when rasterlite2 lib available
            tc.configure_args.append("--with-pcre2={}".format(yes_no(self.options.get_safe("with_pcre2"))))
            tc.configure_args.append("--with-pcre={}".format(yes_no(self.options.get_safe("with_pcre"))))
            tc.configure_args.append("--without-teigha") # commercial library
            tc.configure_args.append("--without-idb") # commercial library
            tc.configure_args.append("--with-webp={}".format(rootpath_no(self.options.with_webp, "libwebp")))
            tc.configure_args.append("--with-geos={}".format(yes_no(self.options.with_geos)))
            tc.configure_args.append("--without-sfcgal") # TODO: to implement when sfcgal lib available
            tc.configure_args.append("--with-qhull={}".format(yes_no(self.options.with_qhull)))
            if self.options.with_opencl:
                tc.configure_args.extend([
                    "--with-opencl",
                    "--with-opencl-include={}".format(unix_path(self, self.dependencies["opencl-headers"].cpp_info.aggregated_components().includedirs[0])),
                    "--with-opencl-lib=-L{}".format(unix_path(self, self.dependencies["opencl-icd-loader"].cpp_info.aggregated_components().libdirs[0]))
                ])
            else:
                tc.configure_args.append("--without-opencl")
            tc.configure_args.append("--with-freexl={}".format(yes_no(self.options.with_freexl)))
            tc.configure_args.append("--with-libjson-c={}".format(rootpath("json-c"))) # always required !
            if self.options.without_pam:
                tc.configure_args.append("--without-pam")
            tc.configure_args.append("--with-poppler={}".format(yes_no(self.options.with_poppler)))
            tc.configure_args.append("--with-podofo={}".format(rootpath_no(self.options.with_podofo, "podofo")))
            if self.options.with_podofo:
                tc.configure_args.append("--with-podofo-lib=-l{}".format(" -l".join(self._gather_libs("podofo"))))
            tc.configure_args.append("--without-pdfium") # TODO: to implement when pdfium lib available
            tc.configure_args.append("--without-perl")
            tc.configure_args.append("--without-python")
            tc.configure_args.append("--without-java")
            tc.configure_args.append("--without-hdfs")
            tc.configure_args.append("--without-tiledb") # TODO: to implement when tiledb lib available
            tc.configure_args.append("--without-mdb")
            tc.configure_args.append("--without-rasdaman") # TODO: to implement when rasdaman lib available
            tc.configure_args.append("--with-brunsli={}".format(yes_no(self.options.with_brunsli)))
            tc.configure_args.append("--without-rdb") # commercial library
            tc.configure_args.append("--without-armadillo") # TODO: to implement when armadillo lib available
            tc.configure_args.append("--with-cryptopp={}".format(rootpath_no(self.options.with_cryptopp, "cryptopp")))
            tc.configure_args.append("--with-crypto={}".format(yes_no(self.options.with_crypto)))
            tc.configure_args.append("--with-lerc={}".format(internal_no(not self.options.without_lerc)))
            if self.options.with_null:
                tc.configure_args.append("--with-null")
            tc.configure_args.append("--with-exr={}".format(yes_no(self.options.with_exr)))
            tc.configure_args.append("--with-heif={}".format(yes_no(self.options.with_heif)))
            tc.generate()

            AutotoolsDeps(self).generate()
            PkgConfigDeps(self).generate()

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_nmake()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            # Required for cross-build to iOS, see https://github.com/OSGeo/gdal/issues/4123
            replace_in_file(self, os.path.join(self.source_folder, "port", "cpl_config.h.in"),
                                  "/* port/cpl_config.h.in",
                                  "#pragma once\n/* port/cpl_config.h.in")
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE.TXT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            with chdir(self, self.source_folder):
                self.run(f"nmake -f makefile.vc devinstall {' '.join(self._nmake_args)}")
            rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "gdalplugins"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GDAL")
        self.cpp_info.set_property("cmake_target_name", "GDAL::GDAL")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "gdal")

        self.cpp_info.includedirs.append(os.path.join("include", "gdal"))
        self.cpp_info.resdirs = ["res"]

        lib_suffix = ""
        if is_msvc(self):
            if self.options.shared:
                lib_suffix += "_i"
            if self.settings.build_type == "Debug":
                lib_suffix += "_d"
        self.cpp_info.libs = [f"gdal{lib_suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi", "ws2_32"])
            if is_msvc(self):
                self.cpp_info.system_libs.append("wbemuuid")
            if self.options.with_odbc and not self.options.shared:
                self.cpp_info.system_libs.extend(["odbc32", "odbccp32"])
                if is_msvc(self):
                    self.cpp_info.system_libs.append("legacy_stdio_definitions")
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

        gdal_data_path = os.path.join(self.package_folder, "res", "gdal")
        self.runenv_info.prepend_path("GDAL_DATA", gdal_data_path)
        if self.options.tools:
            self.buildenv_info.prepend_path("GDAL_DATA", gdal_data_path)

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "GDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "GDAL"
        self.env_info.GDAL_DATA = gdal_data_path
        if self.options.tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
