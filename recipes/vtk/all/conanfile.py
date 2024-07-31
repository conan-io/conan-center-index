# RECIPE MAINTAINER NOTES:
#   There are readme-*.md in the recipe folder.
#
# General recipe design notes: readme-recipe-design.md
# How to add a new version: readme-new-version.md
# How to build a dependency through conan: readme-support-dependency.md

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rmdir, rename, collect_libs
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class VtkConan(ConanFile):
    name = "vtk"
    description = ("The Visualization Toolkit (VTK) by Kitware is an open-source,"
                   " freely available software system for 3D computer graphics,"
                   " image processing, and visualization.")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.vtk.org/"
    topics = ("scientific", "image", "processing", "visualization")
    settings = "os", "compiler", "build_type", "arch"

    short_paths = True
    no_copy_source = True

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        ### compile options ###
        "enable_logging": [True, False],
        ### symmetric multiprocessing ###
        "smp_implementation": ["Sequential", "STDThread", "OpenMP", "TBB"],
        "smp_enable_sequential": [True, False],
        "smp_enable_stdthread": [True, False],
        "smp_enable_openmp": [True, False],
        "smp_enable_tbb": [True, False],
        ### debugging ###
        "debug_modules": [True, False],
        ### external deps ###
        "with_boost": [True, False],
        "with_cgns": [True, False],
        "with_cli11": [True, False],
        "with_cocoa": [True, False],
        "with_dawn": [True, False],
        "with_diy2": [True, False],
        "with_doubleconversion": [True, False],
        "with_eigen": [True, False],
        "with_exodusII": [True, False],
        "with_expat": [True, False],
        "with_exprtk": [True, False],
        "with_fast_float": [True, False],
        "with_ffmpeg": [True, False],
        "with_fmt": [True, False],
        "with_fontconfig": [True, False],
        "with_freetype": [True, False],
        "with_gdal": [True, False],
        "with_gl2ps": [True, False],
        "with_glew": [True, False],
        "with_h5part": [True, False],
        "with_hdf5": [True, False],
        "with_holoplaycore": [True, False],
        "with_ioss": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_jsoncpp": [True, False],
        "with_kissfft": [True, False],
        "with_kwiml": [True, False],
        "with_libarchive": [True, False],
        "with_libharu": [True, False],
        "with_libproj": [True, False],
        "with_libxml2": [True, False],
        "with_loguru": [True, False],
        "with_lz4": [True, False],
        "with_lzma": [True, False],
        "with_metaio": [True, False],
        "with_mpi": [True, False],
        "with_mysql": ["libmysqlclient", "mariadb-connector-c", False],
        "with_netcdf": [True, False],
        "with_nlohmannjson": [True, False],
        "with_octree": [True, False],
        "with_odbc": [True, False],
        "with_ogg": [True, False],
        "with_opencascade": [True, False],
        "with_opengl": [True, False],
        "with_openslide": [True, False],
        "with_openvdb": [True, False],
        "with_openvr": [True, False],
        "with_pdal": [True, False],
        "with_pegtl": [True, False],
        "with_png": [True, False],
        "with_postgresql": [True, False],
        "with_pugixml": [True, False],
        "with_qt": ["5", "6", False],
        "with_sdl2": [True, False],
        "with_sqlite": [True, False],
        "with_theora": [True, False],
        "with_tiff": [True, False],
        "with_utf8": [True, False],
        "with_verdict": [True, False],
        "with_vpic": [True, False],
        "with_x11": [True, False],
        "with_xdmf2": [True, False],
        "with_xdmf3": [True, False],
        "with_zeromq": [True, False],
        "with_zfp": [True, False],
        "with_zlib": [True, False],
        "with_zspace": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        ### compile options ###
        "enable_logging": False,
        ### symmetric multiprocessing ###
        "smp_implementation": "STDThread",
        "smp_enable_sequential": True,
        "smp_enable_stdthread": True,
        "smp_enable_openmp": False,  # TODO: #22360
        "smp_enable_tbb": True,
        ### debugging ###
        "debug_modules": True,
        ### external deps ###
        "with_boost": True,
        "with_cgns": True,
        "with_cli11": True,
        "with_cocoa": True,
        "with_dawn": False,  # TODO: #24735
        "with_diy2": True,
        "with_doubleconversion": True,
        "with_eigen": True,
        "with_exodusII": True,
        "with_expat": True,
        "with_exprtk": True,
        "with_fast_float": True,
        "with_ffmpeg": True,
        "with_fmt": True,
        "with_fontconfig": True,
        "with_freetype": True,
        "with_gdal": False,  # TODO #23233
        "with_gl2ps": True,
        "with_glew": True,
        "with_h5part": True,
        "with_hdf5": True,
        "with_holoplaycore": False,  # not installed correctly
        "with_ioss": True,
        "with_jpeg": "libjpeg",
        "with_jsoncpp": True,
        "with_kissfft": True,
        "with_kwiml": True,
        "with_libarchive": True,
        "with_libharu": True,
        "with_libproj": True,
        "with_libxml2": True,
        "with_loguru": True,
        "with_lz4": True,
        "with_lzma": True,
        "with_metaio": True,
        "with_mpi": False,  # TODO: #18980 Should enable, since disabling this disables all parallel modules
        "with_mysql": "mariadb-connector-c",
        "with_netcdf": True,
        "with_nlohmannjson": True,
        "with_octree": True,
        "with_odbc": True,
        "with_ogg": True,
        "with_opencascade": False,  # very heavy
        "with_opengl": True,
        "with_openslide": False,  # TODO: #21138
        "with_openvdb": True,
        "with_openvr": True,
        "with_pdal": False,  # TODO: #21296
        "with_pegtl": True,
        "with_png": True,
        "with_postgresql": True,
        "with_pugixml": True,
        "with_qt": False,  # TODO: disabled due to too many conflicts
        "with_sdl2": True,
        "with_sqlite": True,
        "with_theora": True,
        "with_tiff": True,
        "with_utf8": True,
        "with_verdict": True,
        "with_vpic": True,
        "with_x11": True,
        "with_xdmf2": True,
        "with_xdmf3": True,
        "with_zeromq": True,
        "with_zfp": True,
        "with_zlib": True,
        "with_zspace": False,  # New zSpace device support, not ready for Linux
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "7",
            "apple-clang": "11",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11
        if not is_apple_os(self):
            del self.options.with_cocoa
        if self.settings.os == "Emscripten":
            del self.options.with_dawn

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # kissfft - we want the double format (also known as kiss_fft_scalar)
        self.options["kissfft"].datatype = "double"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.debug_modules

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.85.0", force=True)
        if self.options.with_cgns:
            self.requires("cgns/4.3.0")
        if self.options.with_cli11:
            self.requires("cli11/2.4.2")
        if self.options.get_safe("with_dawn"):
            self.requires("dawn/cci.20240726")
        if self.options.with_doubleconversion:
            self.requires("double-conversion/3.3.0")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_expat:
            self.requires("expat/[>=2.6.2 <3]")
        if self.options.with_exprtk:
            self.requires("exprtk/0.0.2")
        if self.options.with_fast_float:
            self.requires("fast_float/6.1.3")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.1.1")
        if self.options.with_fmt:
            self.requires("fmt/10.2.1")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.15.0")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_gdal:
            self.requires("gdal/3.8.3")
        if self.options.with_glew:
            self.requires("glew/2.2.0")
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.4.3", force=True)
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.3")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.with_jsoncpp:
            self.requires("jsoncpp/1.9.5")
        if self.options.with_kissfft:
            # FIXME: external kissfft is not picked up by the project
            self.requires("kissfft/131.1.0")
        if self.options.with_libarchive:
            self.requires("libarchive/3.7.4")
        if self.options.with_libharu:
            self.requires("libharu/2.4.4")
        if self.options.with_libproj:
            self.requires("proj/9.3.1")
        if self.options.with_libxml2:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.with_loguru:
            self.requires("loguru/cci.20230406")
        if self.options.with_lz4:
            self.requires("lz4/1.10.0", force=True)
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4.5 <6]")
        if self.options.with_mpi:
            self.requires("openmpi/4.1.6")
        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.1.0")
        elif self.options.with_mysql == "mariadb-connector-c":
            self.requires("mariadb-connector-c/3.3.3")
        if self.options.with_netcdf:
            self.requires("netcdf/4.8.1")
        if self.options.with_nlohmannjson:
            self.requires("nlohmann_json/3.11.3")
        if self.options.with_odbc:
            self.requires("odbc/2.3.11")
        if self.options.with_ogg:
            self.requires("ogg/1.3.5")
        if self.options.with_opencascade:
            self.requires("opencascade/7.6.2")
        if self.options.with_opengl:
            self.requires("opengl/system")
        if self.options.with_openslide:
            self.requires("openslide/0")
        if self.options.with_openvdb:
            self.requires("openvdb/11.0.0")
        if self.options.with_openvr:
            self.requires("openvr/1.16.8")
        if self.options.with_pdal:
            self.requires("pdal/2.3.0")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_postgresql:
            self.requires("libpq/15.5")
        if self.options.with_pugixml:
            self.requires("pugixml/1.14")
        if self.options.with_qt == "5":
            self.requires("qt/[~5.15]")
        elif self.options.with_qt == "6":
            self.requires("qt/[>=6.7 <7]")
        if self.options.with_sdl2:
            self.requires("sdl/2.30.5")
        if self.options.with_sqlite:
            self.requires("sqlite3/3.46.0", force=True)
        if self.options.with_theora:
            self.requires("theora/1.1.1")
        if self.options.with_tiff:
            # Getting jbig linker errors otherwise for some reason
            self.requires("libtiff/4.6.0", options={"jbig": False})
        if self.options.with_utf8:
            self.requires("utfcpp/4.0.4")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")
        if self.options.with_zeromq:
            self.requires("zeromq/4.3.5")
        if self.options.with_zeromq:
            # FIXME: external zfp is not picked up by the project
            self.requires("zfp/1.0.1")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.smp_enable_openmp:
            self.requires("openmp/system")
        if self.options.smp_enable_tbb:
            self.requires("onetbb/2021.12.0", force=True)

        # Not available on CCI
        # ADIOS2 | adios2::adios2
        # DirectX | DirectX::d3d11 DirectX::dxgi | VTK_USE_WIN32_OPENGL
        # HoloPlayCore | HoloPlayCore::HoloPlayCore
        # MEMKIND | MEMKIND::MEMKIND | VTK_USE_MEMKIND
        # OpenImageDenoise | OpenImageDenoise | VTK_ENABLE_OSPRAY AND VTKOSPRAY_ENABLE_DENOISER
        # OpenXR | OpenXR::OpenXR
        # OpenXRRemoting | OpenXR::Remoting
        # VisRTX | VisRTX_DynLoad | VTK_ENABLE_VISRTX
        # catalyst | catalyst::catalyst
        # libLAS | ${libLAS_LIBRARIES}
        # ospray | ospray::ospray | VTK_ENABLE_OSPRAY
        # zSpace | zSpace::zSpace | NOT VTK_ZSPACE_USE_COMPAT_SDK

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.enable_logging and not self.options.with_loguru:
            raise ConanInvalidConfiguration(f"{self.ref} requires with_loguru=True when enable_logging=True")

        if "pugixml" in self.dependencies and self.dependencies["pugixml"].options.wchar_mode:
            raise ConanInvalidConfiguration(f"{self.ref} requires pugixml/*:wchar_mode=False")

        if "kissfft" in self.dependencies and self.dependencies["kissfft"].options.datatype != "double":
            raise ConanInvalidConfiguration(f"{self.ref} requires kissfft/*:datatype=double")

        if self.options.with_qt and not self.dependencies["qt"].options.widgets:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt/*:widgets=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        # No need for versions on installed names
        tc.variables["VTK_VERSIONED_INSTALL"] = False
        # Nothing gets installed without this ON at the moment.
        tc.variables["VTK_INSTALL_SDK"] = True
        # Disabled by default
        tc.variables["VTK_TARGET_SPECIFIC_COMPONENTS"] = False

        # Enable KITs - Quote: "Compiles VTK into a smaller set of libraries."
        # Quote: "Can be useful on platforms where VTK takes a long time to launch due to expensive disk access."
        tc.variables["VTK_ENABLE_KITS"] = False

        # Turn these off for CCI
        tc.variables["VTK_BUILD_TESTING"] = False
        tc.variables["VTK_BUILD_EXAMPLES"] = False
        tc.variables["VTK_BUILD_DOCUMENTATION"] = False
        tc.variables["VTK_BUILD_SPHINX_DOCUMENTATION"] = False

        # TODO: maybe this can be enabled
        tc.variables["VTK_FORBID_DOWNLOADS"] = False

        # Be sure to set this, otherwise vtkCompilerChecks.cmake will downgrade our CXX standard to 11
        tc.variables["VTK_IGNORE_CMAKE_CXX11_CHECKS"] = True

        tc.variables["VTK_ENABLE_CATALYST"] = self.options.get_safe("with_catalyst", False)
        tc.variables["VTK_ENABLE_LOGGING"] = self.options.enable_logging
        tc.variables["VTK_ENABLE_OSPRAY"] = self.options.get_safe("with_ospray", False)
        tc.variables["VTK_ENABLE_WEBGPU"] = True
        tc.variables["VTK_ENABLE_WRAPPING"] = False
        tc.variables["VTK_QT_VERSION"] = self.options.with_qt
        tc.variables["VTK_SMP_ENABLE_OPENMP"] = self.options.smp_enable_openmp
        tc.variables["VTK_SMP_ENABLE_SEQUENTIAL"] = self.options.smp_enable_sequential
        tc.variables["VTK_SMP_ENABLE_STDTHREAD"] = self.options.smp_enable_stdthread
        tc.variables["VTK_SMP_ENABLE_TBB"] = self.options.smp_enable_tbb
        tc.variables["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.smp_implementation
        tc.variables["VTK_USE_COCOA"] = self.options.get_safe("with_cocoa", False)
        tc.variables["VTK_USE_CUDA"] = False  # TODO
        tc.variables["VTK_USE_HIP"] = False  # TODO
        tc.variables["VTK_USE_KOKKOS"] = False
        tc.variables["VTK_USE_MEMKIND"] = False
        tc.variables["VTK_USE_MPI"] = self.options.with_mpi
        tc.variables["VTK_USE_SDL2"] = self.options.with_sdl2
        tc.variables["VTK_USE_TK"] = False  # requires wrap_python
        tc.variables["VTK_USE_X"] = self.options.get_safe("with_x11", False)
        tc.variables["VTK_WRAP_JAVA"] = False
        tc.variables["VTK_WRAP_PYTHON"] = False

        # TODO
        # VTK_ENABLE_VISRTX
        # VTK_ENABLE_VR_COLLABORATION
        # VTK_USE_FUTURE_BOOL
        # VTK_USE_FUTURE_CONST
        # VTK_USE_OPENGL_DELAYED_LOAD
        # VTK_USE_WIN32_OPENGL
        # VTK_ZSPACE_USE_COMPAT_SDK
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS   for video capture
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS_CAPTURE   for video capture
        # TODO try VTK_USE_MICROSOFT_MEDIA_FOUNDATION   for video capture (MP4)

        # print out info about why modules are not available
        if self.options.debug_modules:
            tc.variables["VTK_DEBUG_MODULE"] = True
            tc.variables["VTK_DEBUG_MODULE_ALL"] = True
            tc.variables["VTK_DEBUG_MODULE_building"] = True
            tc.variables["VTK_DEBUG_MODULE_enable"] = True
            tc.variables["VTK_DEBUG_MODULE_kit"] = True
            tc.variables["VTK_DEBUG_MODULE_module"] = True
            tc.variables["VTK_DEBUG_MODULE_provide"] = True
            tc.variables["VTK_DEBUG_MODULE_testing"] = True

        if self.options.with_qt:
            qt = self.dependencies["qt"].options

        modules = {}
        modules["CommonArchive"] = self.options.with_libarchive
        modules["DomainsMicroscopy"] = self.options.with_openslide
        modules["FiltersReebGraph"] = self.options.with_boost
        modules["GUISupportQt"] = self.options.with_qt and qt.opengl != "no"
        modules["GUISupportQtQuick"] = self.options.with_qt and qt.opengl != "no" and qt.gui and qt.qtshadertools and qt.qtdeclarative
        modules["GUISupportQtSQL"] = self.options.with_qt
        modules["GeovisGDAL"] = self.options.with_gdal
        modules["IOADIOS2"] = self.options.get_safe("with_adios2")
        modules["IOCatalystConduit"] = self.options.get_safe("with_catalyst")
        modules["IOFFMPEG"] = self.options.with_ffmpeg
        modules["IOGDAL"] = self.options.with_gdal
        modules["IOLAS"] = self.options.get_safe("with_liblas") and self.options.with_boost
        modules["IOMySQL"] = self.options.with_mysql
        modules["IOOCCT"] = self.options.with_opencascade
        modules["IOODBC"] = self.options.with_odbc
        modules["IOOpenVDB"] = self.options.with_openvdb
        modules["IOPDAL"] = self.options.with_pdal
        modules["IOPostgreSQL"] = self.options.with_postgresql
        modules["InfovisBoost"] = self.options.with_boost
        modules["InfovisBoostGraphAlgorithms"] = self.options.with_boost
        modules["Python"] = False
        modules["RenderingFreeTypeFontConfig"] = self.options.with_fontconfig
        modules["RenderingLookingGlass"] = self.options.with_holoplaycore
        modules["RenderingOpenVR"] = self.options.with_openvr
        modules["RenderingOpenXR"] = self.options.get_safe("with_openxr")
        modules["RenderingOpenXRRemoting"] = self.options.get_safe("with_openxr")
        modules["RenderingQt"] = self.options.with_qt
        modules["RenderingWebGPU"] = self.options.with_sdl2 and self.options.get_safe("with_dawn", True)
        modules["RenderingZSpace"] = self.options.with_zspace
        modules["ViewsQt"] = self.options.with_qt
        modules["cgns"] = self.options.with_cgns
        modules["cli11"] = self.options.with_cli11
        modules["diy2"] = self.options.with_diy2
        modules["doubleconversion"] = self.options.with_doubleconversion
        modules["eigen"] = self.options.with_eigen
        modules["exodusII"] = self.options.with_exodusII
        modules["expat"] = self.options.with_expat
        modules["exprtk"] = self.options.with_exprtk
        modules["fast_float"] = self.options.with_fast_float
        modules["fides"] = self.options.get_safe("with_adios2")
        modules["fmt"] = self.options.with_fmt
        modules["freetype"] = self.options.with_freetype
        modules["gl2ps"] = self.options.with_gl2ps
        modules["glew"] = self.options.with_glew
        modules["h5part"] = self.options.with_h5part
        modules["hdf5"] = self.options.with_hdf5
        modules["ioss"] = self.options.with_ioss
        modules["jpeg"] = self.options.with_jpeg
        modules["jsoncpp"] = self.options.with_jsoncpp
        modules["kissfft"] = self.options.with_kissfft
        modules["kwiml"] = self.options.with_kwiml
        modules["libharu"] = self.options.with_libharu
        modules["libproj"] = self.options.with_libproj
        modules["libxml2"] = self.options.with_libxml2
        modules["loguru"] = self.options.with_loguru
        modules["lz4"] = self.options.with_lz4
        modules["lzma"] = self.options.with_lzma
        modules["metaio"] = self.options.with_metaio
        modules["mpi"] = self.options.with_mpi
        modules["netcdf"] = self.options.with_netcdf
        modules["nlohmannjson"] = self.options.with_nlohmannjson
        modules["octree"] = self.options.with_octree
        modules["ogg"] = self.options.with_ogg
        modules["opengl"] = self.options.with_opengl
        modules["openvr"] = self.options.with_openvr
        modules["pegtl"] = self.options.with_pegtl
        modules["png"] = self.options.with_png
        modules["pugixml"] = self.options.with_pugixml
        modules["qt"] = self.options.with_qt
        modules["sqlite"] = self.options.with_sqlite
        modules["theora"] = self.options.with_theora
        modules["tiff"] = self.options.with_tiff
        modules["utf8"] = self.options.with_utf8
        modules["verdict"] = self.options.with_verdict
        modules["vpic"] = self.options.with_vpic
        modules["xdmf2"] = self.options.with_xdmf2
        modules["xdmf3"] = self.options.with_xdmf3 and self.options.with_boost
        modules["zfp"] = self.options.with_zfp
        modules["zlib"] = self.options.with_zlib

        for pkg, value in modules.items():
            tc.variables[f"VTK_MODULE_ENABLE_VTK_{pkg}"] = "YES" if value else "NO"

        missing_from_cci = {
            "diy2",
            "catalyst"
            "exodusII",
            "fides",
            "gl2ps",
            "h5part",
            "holoplaycore",
            "ioss",
            "kwiml",
            "metaio",
            "mpi4py",
            "octree",
            "pegtl",
            "verdict",
            "vpic",
            "vtkm",
            "xdmf2",
            "xdmf3",
        }
        for pkg in missing_from_cci:
            tc.variables[f"VTK_MODULE_USE_EXTERNAL_VTK_{pkg}"] = False
        tc.variables["VTK_USE_EXTERNAL"] = True

        if self.options.with_netcdf:
            tc.variables["NetCDF_HAS_PARALLEL"] = ""
        if self.options.with_libproj:
            tc.variables["LibPROJ_MAJOR_VERSION"] = Version(self.dependencies["proj"].ref.version).major
        if self.options.with_dawn:
            tc.variables["DAWN_LIBRARIES"] = "dawn::webgpu_dawn"
        tc.generate()

        deps = CMakeDeps(self)

        # allow newer major versions to be used
        deps.set_property("fmt", "cmake_config_version_compat", "AnyNewerVersion")
        deps.set_property("fast_float", "cmake_config_version_compat", "AnyNewerVersion")

        # VTK expects different find_package() filenames and targets (check ThirdParty/LIB/CMakeLists.txt)
        cmake_file_names = {
            "adios2": "ADIOS2",
            "catalyst": "cataylst",
            "expat": "EXPAT",
            "exprtk": "ExprTk",
            "fast_float": "FastFloat",
            "ffmpeg": "FFMPEG",
            "fontconfig": "FontConfig",
            "freetype": "Freetype",
            "gdal": "GDAL",
            "holoplaycore": "HoloPlayCore",
            "libharu": "LibHaru",
            "libmysqlclient": "MySQL",
            "lz4": "LZ4",
            "mariadb-connector-c": "MySQL",
            "memkind": "MEMKIND",
            "netcdf": "NetCDF",
            "openslide": "OpenSlide",
            "openvr": "OpenVR",
            "openxr": "OpenXR",
            "ospray": "ospray",
            "proj": "LibPROJ",
            "theora": "THEORA",
            "xz_utils": "LZMA",
            "zspace": "zSpace",
        }
        cmake_target_names = {
            "adios2": "adios2::adios2",
            "catalyst": "catalyst::catalyst",
            "eigen": "Eigen3::Eigen3",
            "expat": "EXPAT::EXPAT",
            "exprtk": "ExprTk::ExprTk",
            "fast_float": "FastFloat::fast_float",
            "ffmpeg::avcodec": "FFMPEG::avcodec",
            "ffmpeg::avformat": "FFMPEG::avformat",
            "ffmpeg::avutil": "FFMPEG::avutil",
            "ffmpeg::swresample": "FFMPEG::swresample",
            "ffmpeg::swscale": "FFMPEG::swscale",
            "fontconfig": "FontConfig::FontConfig",
            "freetype": "Freetype::Freetype",
            "gdal": "GDAL::GDAL",
            "holoplaycore": "HoloPlayCore::HoloPlayCore",
            "libharu": "LibHaru::LibHaru",
            "libmysqlclient": "MySQL::MySQL",
            "lz4": "LZ4::LZ4",
            "mariadb-connector-c": "MySQL::MySQL",
            "memkind": "MEMKIND::MEMKIND",
            "netcdf": "NetCDF::NetCDF",
            "openslide": "OpenSlide::OpenSlide",
            "openvr": "OpenVR::OpenVR",
            "openxr": "OpenXR::OpenXR",
            "ospray": "ospray::ospray",
            "proj": "LibPROJ::LibPROJ",
            "sdl2": "SDL2::SDL2",
            "theora": "THEORA::THEORA",
            "theora::theoradec": "THEORA::DEC",
            "theora::theoraenc": "THEORA::ENC",
            "utfcpp": "utf8cpp::utf8cpp",
            "xz_utils": "LZMA::LZMA",
            "zspace": "zSpace::zSpace",
        }
        for dep, file_name in cmake_file_names.items():
            deps.set_property(dep, "cmake_file_name", file_name)
        for dep, target_name in cmake_target_names.items():
            deps.set_property(dep, "cmake_target_name", target_name)

        # double-version has their headers in <double-conversion/header> but VTK expects just <header>
        # TODO: this is not allowed, should patch instead
        if self.options.with_doubleconversion:
            double_conversion = self.dependencies["double-conversion"].cpp_info
            double_conversion.includedirs[0] = os.path.join(double_conversion.includedirs[0], "double-conversion")

        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # VTK installs the licenses under the share/licenses/VTK directory, move it
        rename(self, os.path.join(self.package_folder, "share", "licenses", "VTK"),
               os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # delete VTK-installed cmake files
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VTK")
        self.cpp_info.set_property("cmake_target_name", "VTK::VTK")
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "vtk"))
