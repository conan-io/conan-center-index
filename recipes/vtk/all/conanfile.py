# RECIPE MAINTAINER NOTES:
#   There are readme-*.md in the recipe folder.
#
# General recipe design notes: readme-recipe-design.md
# How to add a new version: readme-new-version.md
# How to build a dependency through conan: readme-support-dependency.md
import functools
import itertools
import json
import os
import re
from collections import OrderedDict
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import export_conandata_patches, get, rmdir, rename, replace_in_file, load, save, copy
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
        "with_diy2": [True, False],
        "with_eigen": [True, False],
        "with_exodusII": [True, False],
        "with_expat": [True, False],
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
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg", False],
        "with_jsoncpp": [True, False],
        "with_libharu": [True, False],
        "with_libproj": [True, False],
        "with_libxml2": [True, False],
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
        "with_qt": ["5", "6", False],
        "with_sdl2": [True, False],
        "with_sqlite": [True, False],
        "with_theora": [True, False],
        "with_tiff": [True, False],
        "with_verdict": [True, False],
        "with_vpic": [True, False],
        "with_x11": [True, False],
        "with_xdmf2": [True, False],
        "with_xdmf3": [True, False],
        "with_zeromq": [True, False],
        "with_zfp": [True, False],
        "with_zspace": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        ### compile options ###
        "enable_logging": True,
        ### symmetric multiprocessing ###
        "smp_implementation": "STDThread",
        "smp_enable_sequential": True,
        "smp_enable_stdthread": True,
        "smp_enable_openmp": True,  # TODO: #22360
        "smp_enable_tbb": True,
        ### debugging ###
        "debug_modules": True,
        ### external deps ###
        "with_boost": True,
        "with_cgns": True,
        "with_cli11": True,
        "with_cocoa": True,
        "with_diy2": True,
        "with_eigen": True,
        "with_exodusII": True,
        "with_expat": True,
        "with_ffmpeg": True,
        "with_fmt": True,
        "with_fontconfig": True,
        "with_freetype": True,
        "with_gdal": True,  # TODO #23233
        "with_gl2ps": True,
        "with_glew": True,
        "with_h5part": True,
        "with_hdf5": True,
        "with_holoplaycore": True,  # not installed correctly
        "with_ioss": True,
        "with_jpeg": "libjpeg",
        "with_jsoncpp": True,
        "with_libharu": True,
        "with_libproj": True,
        "with_libxml2": True,
        "with_metaio": True,
        "with_mpi": True,  # TODO: #18980 Should enable, since disabling this disables all parallel modules
        "with_mysql": "mariadb-connector-c",
        "with_netcdf": True,
        "with_nlohmannjson": True,
        "with_octree": True,
        "with_odbc": True,
        "with_ogg": True,
        "with_opencascade": True,  # very heavy
        "with_opengl": True,
        "with_openslide": True,  # TODO: #21138
        "with_openvdb": True,
        "with_openvr": True,
        "with_pdal": True,  # TODO: #21296
        "with_pegtl": True,
        "with_png": True,
        "with_postgresql": True,
        "with_qt": "6",  # TODO: disabled due to too many conflicts
        "with_sdl2": True,
        "with_sqlite": True,
        "with_theora": True,
        "with_tiff": True,
        "with_verdict": True,
        "with_vpic": True,
        "with_x11": True,
        "with_xdmf2": True,
        "with_xdmf3": True,
        "with_zeromq": True,
        "with_zfp": True,
        "with_zspace": True,  # New zSpace device support, not ready for Linux
    }
    # NOTE: all non-third-party VTK modules are also available as options.
    # e.g. "IOGeoJSON": ["auto", "YES", "WANT", "DONT_WANT", "NO"], etc.
    # See options/<version>.json for the full list of modules.
    # Keep in mind that there is almost no validation done for compatibility between the module options.
    # We mostly rely on the checks done in the configure phase of the CMake build instead.

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

    def export(self):
        copy(self, "*.json", self.recipe_folder, self.export_folder)

    @property
    def _modules_from_all_versions(self):
        # Modules from all versions
        all_modules = set()
        for options_json in Path(self.recipe_folder, "options").glob("*.json"):
            all_modules.update(json.loads(options_json.read_text())["modules"])
        return sorted(all_modules)

    def init(self):
        all_modules = self._modules_from_all_versions
        new_options = {mod: ["auto", "YES", "WANT", "DONT_WANT", "NO"] for mod in all_modules}
        new_defaults = {mod: "auto" for mod in all_modules}
        self.options.update(new_options, new_defaults)

    @property
    @functools.lru_cache()
    def _module_opts(self):
        return json.loads(Path(self.recipe_folder, "options", f"{self.version}.json").read_text())["modules"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            # Uses windows.h
            del self.options.with_zspace
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11
        if not is_apple_os(self):
            del self.options.with_cocoa
        if self.settings.os == "Emscripten":
            self.options.rm_safe("with_dawn")
        for opt in set(self._modules_from_all_versions) - set(self._module_opts):
            self.options.rm_safe(opt)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # kissfft - we want the double format (also known as kiss_fft_scalar)
        self.options["kissfft"].datatype = "double"
        self.options["pugixml"].wchar_mode = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.debug_modules

    def requirements(self):
        # Always required by CommonArchive, CommonCore, CommonMath, CommonDataModel, CommonMisc, IOCore
        self.requires("double-conversion/3.3.0")
        self.requires("exprtk/0.0.2")
        self.requires("fast_float/6.1.3")
        self.requires("kissfft/131.1.0")
        self.requires("libarchive/3.7.4")
        self.requires("lz4/1.10.0", force=True)
        self.requires("pugixml/1.14")
        self.requires("utfcpp/4.0.4")
        self.requires("xz_utils/[>=5.4.5 <6]")
        self.requires("zlib/[>=1.2.11 <2]")

        # The project uses modified loguru for logging, which cannot be unvendored

        if self.options.with_boost:
            self.requires("boost/1.85.0", force=True)
        if self.options.with_cgns:
            self.requires("cgns/4.3.0")
        if self.options.with_cli11:
            self.requires("cli11/2.4.2")
        if self.options.get_safe("with_dawn"):
            # Dawn option has been disabled because its support is still very experimental.
            # https://gitlab.kitware.com/vtk/vtk/-/blob/v9.3.1/Rendering/WebGPU/README.md?ref_type=tags#how-to-build-vtk-with-dawn-highly-experimental
            # Dawn recipe is not yet merged: #24735
            self.requires("dawn/cci.20240726")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_expat:
            self.requires("expat/[>=2.6.2 <3]")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.1.1")
        if self.options.with_fmt:
            self.requires("fmt/10.2.1")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.15.0", force=True)
        if self.options.with_freetype:
            self.requires("freetype/2.13.0", force=True)
        if self.options.with_gdal:
            self.requires("gdal/3.9.1", force=True)
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
        if self.options.with_libharu:
            self.requires("libharu/2.4.4")
        if self.options.with_libproj:
            self.requires("proj/9.3.1")
        if self.options.with_libxml2:
            self.requires("libxml2/[>=2.12.5 <3]", force=True)
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
            self.requires("openslide/4.0.0")
        if self.options.with_openvdb:
            self.requires("openvdb/11.0.0")
        if self.options.with_openvr:
            self.requires("openvr/1.16.8")
        if self.options.with_pdal:
            self.requires("pdal/2.7.2")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]", force=True)
        if self.options.with_postgresql:
            self.requires("libpq/15.5", force=True)
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
            self.requires("libtiff/4.6.0")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")
        if self.options.with_zeromq:
            self.requires("zeromq/4.3.5")
        if self.options.with_zeromq:
            self.requires("zfp/1.0.1")
        if self.options.smp_enable_openmp:
            self.requires("openmp/system")
        if self.options.smp_enable_tbb:
            self.requires("onetbb/2021.12.0", force=True)

        self.requires("glib/2.78.3", override=True)
        self.requires("hwloc/2.10.0", override=True)
        self.requires("xkbcommon/1.6.0", override=True)

        # Not available on CCI
        # vtk-dicom
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
        # zSpace | zSpace::zSpace

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.dependencies["pugixml"].options.wchar_mode:
            raise ConanInvalidConfiguration(f"{self.ref} requires pugixml/*:wchar_mode=False")

        if self.dependencies["kissfft"].options.datatype != "double":
            raise ConanInvalidConfiguration(f"{self.ref} requires kissfft/*:datatype=double")

        if self.options.with_qt and not self.dependencies["qt"].options.widgets:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt/*:widgets=True")

        if self.options.with_mysql and not self.options.with_sqlite:
            raise ConanInvalidConfiguration(f"{self.ref} requires with_sqlite=True when with_mysql=True")

        if self.options.get_safe("with_liblas") and not self.options.with_boost:
            raise ConanInvalidConfiguration(f"{self.ref} requires with_boost=True when with_liblas=True")

        if self.options.with_xdmf3 and not self.options.with_boost:
            raise ConanInvalidConfiguration(f"{self.ref} requires with_boost=True when with_xdmf3=True")

        # Just to check for conflicts
        self._compute_module_values()

    @functools.lru_cache()
    def _compute_module_values(self):
        if self.options.with_qt:
            qt = self.dependencies["qt"].options

        def _want_no(value):
            return "WANT" if value else "NO"

        def _yes_no(value):
            return "YES" if value else "NO"

        modules = {}
        # The common modules and their dependencies should always be available
        modules["CommonArchive"] = "YES"
        modules["CommonColor"] = "YES"
        modules["CommonComputationalGeometry"] = "YES"
        modules["CommonCore"] = "YES"
        modules["CommonDataModel"] = "YES"
        modules["CommonExecutionModel"] = "YES"
        modules["CommonMath"] = "YES"
        modules["CommonMisc"] = "YES"
        modules["CommonPython"] = "NO"
        modules["CommonSystem"] = "YES"
        modules["CommonTransforms"] = "YES"
        modules["IOCore"] = "YES"
        modules["DomainsMicroscopy"] = _want_no(self.options.with_openslide)
        modules["FiltersReebGraph"] = _want_no(self.options.with_boost)
        modules["GUISupportQt"] = _want_no(self.options.with_qt and qt.opengl != "no")
        modules["GUISupportQtQuick"] = _want_no(self.options.with_qt and qt.opengl != "no" and qt.gui and qt.qtshadertools and qt.qtdeclarative)
        modules["GUISupportQtSQL"] = _want_no(self.options.with_qt)
        modules["GeovisGDAL"] = _want_no(self.options.with_gdal)
        modules["IOADIOS2"] = _yes_no(self.options.get_safe("with_adios2"))
        modules["IOCatalystConduit"] = _yes_no(self.options.get_safe("with_catalyst"))
        modules["IOFFMPEG"] = _yes_no(self.options.with_ffmpeg)
        modules["IOGDAL"] = _yes_no(self.options.with_gdal)
        modules["IOLAS"] = _yes_no(self.options.get_safe("with_liblas") and self.options.with_boost)
        modules["IOMySQL"] = _yes_no(self.options.with_mysql and self.options.with_sqlite)
        modules["IOOCCT"] = _yes_no(self.options.with_opencascade)
        modules["IOODBC"] = _yes_no(self.options.with_odbc)
        modules["IOOpenVDB"] = _yes_no(self.options.with_openvdb)
        modules["IOPDAL"] = _yes_no(self.options.with_pdal)
        modules["IOPostgreSQL"] = _yes_no(self.options.with_postgresql)
        modules["InfovisBoost"] = _yes_no(self.options.with_boost)
        modules["InfovisBoostGraphAlgorithms"] = _want_no(self.options.with_boost)
        modules["Python"] = "NO"
        modules["RenderingFreeTypeFontConfig"] = _want_no(self.options.with_fontconfig)
        modules["RenderingLookingGlass"] = _want_no(self.options.with_holoplaycore)
        modules["RenderingOpenVR"] = _want_no(self.options.with_openvr)
        modules["RenderingOpenXR"] = _want_no(self.options.get_safe("with_openxr"))
        modules["RenderingOpenXRRemoting"] = _want_no(self.options.get_safe("with_openxr"))
        modules["RenderingQt"] = _want_no(self.options.with_qt)
        modules["RenderingWebGPU"] = _want_no(self.options.with_sdl2 and (self.settings.os == "Emscripten" or self.options.get_safe("with_dawn")))
        modules["RenderingZSpace"] = _want_no(self.options.get_safe("with_zspace"))
        modules["ViewsQt"] = _want_no(self.options.with_qt)
        modules["cgns"] = _yes_no(self.options.with_cgns)
        modules["cli11"] = _yes_no(self.options.with_cli11)
        modules["diy2"] = _yes_no(self.options.with_diy2)
        modules["doubleconversion"] = "YES"
        modules["eigen"] = _yes_no(self.options.with_eigen)
        modules["exodusII"] = _yes_no(self.options.with_exodusII)
        modules["expat"] = _yes_no(self.options.with_expat)
        modules["exprtk"] = "YES"
        modules["fast_float"] = "YES"
        modules["fides"] = _yes_no(self.options.get_safe("with_adios2"))
        modules["fmt"] = _yes_no(self.options.with_fmt)
        modules["freetype"] = _yes_no(self.options.with_freetype)
        modules["gl2ps"] = _yes_no(self.options.with_gl2ps)
        modules["glew"] = _yes_no(self.options.with_glew)
        modules["h5part"] = _yes_no(self.options.with_h5part)
        modules["hdf5"] = _yes_no(self.options.with_hdf5)
        modules["ioss"] = _yes_no(self.options.with_ioss)
        modules["jpeg"] = _yes_no(self.options.with_jpeg)
        modules["jsoncpp"] = _yes_no(self.options.with_jsoncpp)
        modules["kissfft"] = "YES"
        modules["kwiml"] = "YES"
        modules["libharu"] = _yes_no(self.options.with_libharu)
        modules["libproj"] = _yes_no(self.options.with_libproj)
        modules["libxml2"] = _yes_no(self.options.with_libxml2)
        modules["loguru"] = _yes_no(self.options.enable_logging)
        modules["lz4"] = "YES"
        modules["lzma"] = "YES"
        modules["metaio"] = _yes_no(self.options.with_metaio)
        modules["mpi"] = _yes_no(self.options.with_mpi)
        modules["netcdf"] = _yes_no(self.options.with_netcdf)
        modules["nlohmannjson"] = _yes_no(self.options.with_nlohmannjson)
        modules["octree"] = _yes_no(self.options.with_octree)
        modules["ogg"] = _yes_no(self.options.with_ogg)
        modules["opengl"] = _yes_no(self.options.with_opengl)
        modules["openvr"] = _yes_no(self.options.with_openvr)
        modules["pegtl"] = _yes_no(self.options.with_pegtl)
        modules["png"] = _yes_no(self.options.with_png)
        modules["pugixml"] = "YES"
        modules["qt"] = _yes_no(self.options.with_qt)
        modules["sqlite"] = _yes_no(self.options.with_sqlite)
        modules["theora"] = _yes_no(self.options.with_theora)
        modules["tiff"] = _yes_no(self.options.with_tiff)
        modules["utf8"] = "YES"
        modules["verdict"] = _yes_no(self.options.with_verdict)
        modules["vpic"] = _yes_no(self.options.with_vpic)
        modules["xdmf2"] = _yes_no(self.options.with_xdmf2)
        modules["xdmf3"] = _yes_no(self.options.with_xdmf3 and self.options.with_boost)
        modules["zfp"] = _yes_no(self.options.with_zfp)
        modules["zlib"] = "YES"

        for mod in self._module_opts:
            if self.options.get_safe(mod) != "auto":
                value = self.options.get_safe(mod)
                if mod in modules and modules[mod] != value and modules[mod] != "WANT":
                    raise ConanInvalidConfiguration(f"Option '{mod}={value}' conflicts with value '{modules[mod]}' computed from 'with_*' options.")
                modules[mod] = value

        return modules

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.with_qt:
            # Qt's moc command fails to find libpcre2-16.so.0 otherwise
            VirtualRunEnv(self).generate(scope="build")

        tc = CMakeToolchain(self)

        # No need for versions on installed names
        tc.variables["VTK_VERSIONED_INSTALL"] = False
        # Nothing gets installed without this ON at the moment.
        tc.variables["VTK_INSTALL_SDK"] = True

        # TODO: Enable KITs - Quote: "Compiles VTK into a smaller set of libraries."
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
        tc.variables["VTK_ENABLE_VR_COLLABORATION"] = self.options.with_zeromq
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

        for pkg, value in self._compute_module_values().items():
            tc.variables[f"VTK_MODULE_ENABLE_VTK_{pkg}"] = value

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
        tc.generate()

        deps = CMakeDeps(self)

        # allow newer major versions to be used
        deps.set_property("fast_float", "cmake_config_version_compat", "AnyNewerVersion")
        deps.set_property("fmt", "cmake_config_version_compat", "AnyNewerVersion")
        deps.set_property("qt", "cmake_config_version_compat", "AnyNewerVersion")

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
            "ogg": "OGG",
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
            "ogg": "OGG::OGG",
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
        double_conversion = self.dependencies["double-conversion"].cpp_info
        double_conversion.includedirs[0] = os.path.join(double_conversion.includedirs[0], "double-conversion")

        deps.generate()

        # Store a mapping from CMake to Conan targets for later use in package_info()
        targets_map = self._get_cmake_to_conan_targets_map(deps)
        save(self, self._cmake_targets_map_json, json.dumps(targets_map, indent=2))

    @property
    def _cmake_targets_map_json(self):
        return os.path.join(self.generators_folder, "cmake_to_conan_targets.json")

    @property
    @functools.lru_cache()
    def _cmake_targets_map(self):
        return json.loads(load(self, self._cmake_targets_map_json))

    def _get_cmake_to_conan_targets_map(self, deps):
        """
        Returns a dict of Conan targets corresponding to generated CMake targets. E.g.:
         'WebP::webpdecoder': 'libwebp::webpdecoder',
         'WebP::webpdemux': 'libwebp::webpdemux',
         'ZLIB::ZLIB': 'zlib::zlib',
        """
        def _get_targets(*args):
            targets = [deps.get_property("cmake_target_name", *args),
                       deps.get_property("cmake_module_target_name", *args)]
            targets += deps.get_property("cmake_target_aliases", *args) or []
            return list(filter(None, targets))

        cmake_targets_map = {}
        for req, dependency in self.dependencies.host.items():
            dep_name = req.ref.name
            for target in _get_targets(dependency):
                cmake_targets_map[target] = f"{dep_name}::{dep_name}"
            for component, _ in dependency.cpp_info.components.items():
                for target in _get_targets(dependency, component):
                    cmake_targets_map[target] = f"{dep_name}::{component}"

        # System recipes need special handling since they rely on CMake's Find<Package> modules
        cmake_targets_map.update({
            "OpenMP::OpenMP_C": "openmp::openmp",
            "OpenMP::OpenMP_CXX": "openmp::openmp",
            "OpenGL::EGL": "egl::egl",
            "OpenGL::GL": "opengl::opengl",
            "OpenGL::GLES2": "opengl::opengl",
            "OpenGL::GLES3": "opengl::opengl",
            "OpenGL::GLU": "glu::glu",
            "OpenGL::GLX": "opengl::opengl",
            "OpenGL::OpenGL": "opengl::opengl",
            "X11::X11": "xorg::x11",
            "X11::Xcursor": "xorg::xcursor",
        })
        return cmake_targets_map

    def _patch_remote_modules(self):
        # These are only available after cmake.configure()
        path = os.path.join(self.source_folder, "Remote", "MomentInvariants", "MomentInvariants", "vtkComputeMoments.cxx")
        if os.path.exists(path):
            replace_in_file(self, path, "tools/kiss_fftnd.h", "kiss_fftnd.h")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        self._patch_remote_modules()
        cmake.build()

    def _parse_cmake_targets(self, targets_file):
        # Parse info from VTK-targets.cmake
        # Example:
        #   add_library(VTK::IOOggTheora SHARED IMPORTED)
        #   set_target_properties(VTK::IOOggTheora PROPERTIES
        #   INTERFACE_COMPILE_DEFINITIONS "VTK_HAS_OGGTHEORA_SUPPORT"
        #   INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include/vtk"
        #   INTERFACE_LINK_LIBRARIES "VTK::CommonExecutionModel;VTK::IOMovie"
        #   )
        # The following properties are set by the project:
        #   compile_definitions
        #   compile_features (only sets CXX_STANDARD)
        #   include_directories (always "${_IMPORT_PREFIX}/include/vtk")
        #   link_libraries
        #   system_include_directories (still include/vtk, but silent)
        txt = load(self, targets_file)
        raw_targets = re.findall(r"add_library\(VTK::(\S+) (\S+) IMPORTED\)", txt)
        targets = {name: {"is_interface": kind == "INTERFACE"} for name, kind in raw_targets if name not in ["vtkbuild"]}
        props_raw = re.findall(r"set_target_properties\(VTK::(\S+) PROPERTIES\n((?: *.+\n)+)\)", txt)
        for name, body in props_raw:
            for prop, value in re.findall(r"^ *INTERFACE_(\w+)\b \"(.+)\"$", body, re.M):
                value = value.split(";")
                targets[name][prop.lower()] = value
        return targets

    @staticmethod
    def _strip_prefix(name):
        if name.startswith("VTK::"):
            return name[5:]

    def _get_info_from_modules_json(self, modules_json):
        modules = json.loads(load(self, modules_json))["modules"]
        return {
            self._strip_prefix(module): {
                "deps": list(map(self._strip_prefix, mod_info.get("depends", []) + mod_info.get("private_depends", []))),
                "lib_name": mod_info.get("library_name"),
                "implementable": mod_info.get("implementable", False),
                "implements": list(map(self._strip_prefix, mod_info.get("implements", []))),
            }
            for module, mod_info in modules.items()
        }

    def _is_matching_cmake_platform(self, platform_id):
        if platform_id == "Darwin":
            return is_apple_os(self)
        if platform_id == "Linux":
            return self.settings.os in ["Linux", "FreeBSD"]
        if platform_id in ["WIN32", "Windows"]:
            return self.settings.os == "Windows"
        if platform_id == "MinGW":
            return self.settings.os == "Windows" and self.settings.compiler == "gcc"
        if platform_id in ["Android", "Emscripten", "SunOS"]:
            return self.settings.os == platform_id
        raise ConanException(f"Unexpected CMake PLATFORM_ID: '{platform_id}'")

    def _cmake_target_to_conan_requirement(self, target):
        if target.startswith("VTK::"):
            # Internal target
            return target[5:]
        else:
            # External target
            req = self._cmake_targets_map.get(target, target)
            if not req:
                raise ConanException(f"Unexpected CMake target: '{target}'")
            return req

    @property
    def _known_system_libs(self):
        return ["m", "dl", "pthread", "rt", "log", "embind", "socket", "nsl", "wsock32", "ws2_32"]

    def _transform_link_libraries(self, values):
        # Converts a list of LINK_LIBRARIES values into a list of component requirements, system_libs and frameworks.
        requires = []
        system_libs = []
        frameworks = []
        for v in values:
            # strip "\$<LINK_ONLY:FontConfig::FontConfig>" etc.
            v = re.sub(r"^\\\$<LINK_ONLY:(.*)>$", r"\1", v)
            if not v:
                continue
            if "-framework " in v:
                frameworks += re.findall(r"-framework (\S+)", v)
            elif "PLATFORM_ID" in v:
                # e.g. "\$<\$<PLATFORM_ID:WIN32>:wsock32>"
                platform_id = re.search(r"PLATFORM_ID:(\w+)", v).group(1)
                if self._is_matching_cmake_platform(platform_id):
                    lib = re.search(":(.+)>$", v).group(1)
                    system_libs.append(lib)
            elif v.lower().replace(".lib", "") in self._known_system_libs:
                system_libs.append(v)
            elif v == "Threads::Threads":
                if self.settings.os in ["Linux", "FreeBSD"]:
                    system_libs.append("pthread")
            else:
                requires.append(self._cmake_target_to_conan_requirement(v))
        return requires, system_libs, frameworks

    @property
    def _lib_suffix(self):
        return "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

    @staticmethod
    def _remove_duplicates(values):
        return list(OrderedDict.fromkeys(values))

    def _cmake_targets_to_conan_components(self, targets_info, modules_info):
        # Fill in components based on VTK-targets.cmake and modules.json
        components = {}
        for name, target_info in targets_info.items():
            module_info = modules_info.get(name, {})
            component = {}
            if not target_info["is_interface"]:
                default_libname = f"vtk{name}" if not name.startswith("vtk") else name
                lib = module_info.get("lib_name", default_libname)
                component["libs"] = [lib + self._lib_suffix]
            for definition in target_info.get("compile_definitions", []):
                if definition.startswith("-D"):
                    definition = definition[2:]
                if not "defines" in component:
                    component["defines"] = []
                component["defines"].append(definition)
            requires, system_libs, frameworks = self._transform_link_libraries(target_info.get("link_libraries", []))
            requires += module_info.get("deps", [])
            if name in requires:
                # Only VTK::pugixml has this issue as of v9.3.1
                self.output.warning(f"CMake target VTK::{name} has a circular dependency on itself")
                requires = [req for req in requires if req != name]
            if requires:
                component["requires"] = self._remove_duplicates(requires)
            if system_libs:
                component["system_libs"] = self._remove_duplicates(system_libs)
            if frameworks:
                component["frameworks"] = self._remove_duplicates(frameworks)
            if module_info.get("implementable", False):
                component["implementable"] = True
            implements = module_info.get("implements", [])
            if implements:
                component["implements"] = implements
            components[name] = component
        return components

    @property
    def _components_json(self):
        return os.path.join(self.package_folder, "share", "conan_components.json")

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # VTK installs the licenses under the share/licenses/VTK directory, move it
        rename(self, os.path.join(self.package_folder, "share", "licenses", "VTK"),
               os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # Parse the VTK-targets.cmake file to generate Conan components
        targets_config = os.path.join(self.package_folder, "lib", "cmake", "vtk", "VTK-targets.cmake")
        cmake_target_props = self._parse_cmake_targets(targets_config)
        # Need to parse modules.json as well because private deps are missing from VTK-targets.cmake
        modules_json = os.path.join(self.build_folder, "modules.json")
        modules_info = self._get_info_from_modules_json(modules_json)
        # Generate components info for package_info()
        components = self._cmake_targets_to_conan_components(cmake_target_props, modules_info)
        save(self, self._components_json, json.dumps(components, indent=2))

        # Write autoinit headers
        self._generate_autoinits(modules_info)

        # create a cmake module with our special variables
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        cmake_module_path = os.path.join(self.package_folder, "lib", "cmake", "vtk", "conan-official-vtk-variables.cmake")
        save(self, cmake_module_path, "set(VTK_ENABLE_KITS FALSE)\n")

    def _generate_autoinits(self, modules_info):
        ### VTK AUTOINIT ###
        # VTK has a special factory registration system, and modules that implement others have to be registered.
        # This mechanism was encoded into VTK's cmake autoinit system, which we (probably) can't use in a conan context.
        # So, we will implement the required autoinit registration things here.
        #
        # This recipe will ultimately generate special header files that contain lines like:
        #   #define vtkRenderingCore_AUTOINIT 2(vtkRenderingFreeType, vtkInteractionStyle)
        #       (this module is implemented)              (by these modules)
        #            IMPLEMENTABLE         by                 IMPLEMENTS
        #
        # There is one header per implementable module, and each user of an implementing-module must
        # have a special #define that tells the VTK system where this header is.  The header will be
        # included into the compilation and the autoinit system will register the implementing-module.
        #
        # But the trick is the library consumer will only declare they want to use an implementing module
        # (eg vtkRenderingOpenGL2) but will not use that module directly.
        # Instead, they will only use vtkRenderingCore and expect the OpenGL2 module to be magically built
        # by the core factory.  OpenGL2 module has to register with the Core module, without the library
        # consumer specifically calling the registration.
        #
        # VTK's cmake seems to generate headers for different combinations of components,
        #   so they need to create a unique autoinit file when a downstream consumer calls cmake function
        #   vtk_module_autoinit(TARGETS <target>... MODULES <module>...), so each target must know ALL
        #   of the vtk modules they will use (at cmake-time), and a unique header will be made for that combination.
        #  That header will be #included via a clever define for that target.
        #
        # This won't work in our case, and that would only work for cmake consumers.
        #
        # So I'm going to try a different approach:
        #  * define a header for all possible combinations of implementer-modules for an implementable-module.
        #  * use a define for each of the implementer-modules.  If a target is using that implementer-module,
        #     it will activate the autoinit for that module thanks to the #define flag
        #
        # Also note we have to be clever with the ordering of the combinations, as we only want to pick ONE of the combos.
        #
        # The max number of implementer combinations as of v9.3.1 is 2^7 - 1 = 127 for RenderingCore, which is tolerable.
        #
        # Example of an autoinit file with two implementers:
        ##  #if 0
        ##
        ##  #elif defined(VTK_CONAN_WANT_AUTOINIT_vtkRenderingOpenGL2) && defined(VTK_CONAN_WANT_AUTOINIT_vtkInteractionStyle)
        ##  #  define vtkRenderingCore_AUTOINIT 2(vtkRenderingOpenGL2,vtkInteractionStyle)
        ##
        ##  #elif defined(VTK_CONAN_WANT_AUTOINIT_vtkRenderingOpenGL2)
        ##  #  define vtkRenderingCore_AUTOINIT 1(vtkRenderingOpenGL2)
        ##
        ##  #elif defined(VTK_CONAN_WANT_AUTOINIT_vtkInteractionStyle)
        ##  #  define vtkRenderingCore_AUTOINIT 1(vtkInteractionStyle)
        ##
        ##  #endif

        # Gather all implementers for each implementable module
        autoinits = {mod: set() for mod, info in modules_info.items() if info["implementable"]}
        for module_name, module_info in modules_info.items():
            for implementable in module_info["implements"]:
                autoinits[implementable].add(module_name)
        # Write those special autoinit header files
        for implementable, all_implementers in autoinits.items():
            self.output.debug(f"Generating autoinit headers for {implementable} with ({', '.join(all_implementers)}) implementers")
            all_implementers = [f"vtk{impl}" for impl in sorted(all_implementers)]
            content = "#if 0\n\n"
            for L in range(len(all_implementers), 0, -1):
                for combination in itertools.combinations(all_implementers, L):
                    content += f"#elif {' && '.join(f'defined(VTK_CONAN_WANT_AUTOINIT_{comp})' for comp in combination)}\n"
                    content += f"#  define vtk{implementable}_AUTOINIT {L}({','.join(combination)})\n\n"
            content += "#endif\n"
            autoinit_file = os.path.join(self.package_folder, "include", "vtk", "vtk-conan", f"vtk_autoinit_vtk{implementable}.h")
            save(self, autoinit_file, content)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VTK")

        cmake_modules_dir = os.path.join("lib", "cmake", "vtk")
        cmake_module_path = os.path.join(cmake_modules_dir, "conan-official-vtk-variables.cmake")
        self.cpp_info.builddirs = [cmake_modules_dir]
        self.cpp_info.set_property("cmake_build_modules", [cmake_module_path])

        # Define components based on the .json file generated in package()
        components = json.loads(load(self, self._components_json))
        for name, info in components.items():
            component = self.cpp_info.components[name]
            component.set_property("cmake_target_name", f"VTK::{name}")
            component.includedirs = [os.path.join("include", "vtk")]
            component.libs = info.get("libs", [])
            component.defines = info.get("defines", [])
            component.requires = info.get("requires", [])
            component.system_libs = info.get("system_libs", [])
            component.frameworks = info.get("frameworks", [])
            # Add any required autoinit definitions for this component
            for implementable in info.get("implements", []):
                component.defines.append(f'vtk{implementable}_AUTOINIT_INCLUDE="vtk-conan/vtk_autoinit_vtk{implementable}.h"')
                component.defines.append(f"VTK_CONAN_WANT_AUTOINIT_vtk{name}")

        # Add some missing private dependencies
        self.cpp_info.components["pugixml"].requires.append("pugixml::pugixml")
        self.cpp_info.components["CommonArchive"].requires.append("libarchive::libarchive")
        if self.options.get_safe("with_memkind"):
            self.cpp_info.components["CommonCore"].requires.append("memkind::memkind")
        if self.options.smp_enable_tbb:
            self.cpp_info.components["CommonCore"].requires.append("onetbb::libtbb")
        if self.options.smp_enable_openmp:
            self.cpp_info.components["CommonCore"].requires.append("openmp::openmp")
        if "DomainsMicroscopy" in components:
            self.cpp_info.components["DomainsMicroscopy"].requires.append("openslide::openslide")
        if "GeovisGDAL" in components:
            self.cpp_info.components["GeovisGDAL"].requires.append("gdal::gdal")
        if "GUISupportQt" in components:
            self.cpp_info.components["GUISupportQt"].requires.extend(["qt::qtOpenGL", "qt::qtWidgets", "qt::qtOpenGLWidgets"])
        if "GUISupportQtQuick" in components:
            self.cpp_info.components["GUISupportQtQuick"].requires.extend(["qt::qtGui", "qt::qtOpenGL", "qt::qtQuick", "qt::qtQml"])
        if "GUISupportQtSQL" in components:
            self.cpp_info.components["GUISupportQtSQL"].requires.extend(["qt::qtWidgets", "qt::qtSql"])
        if "InfovisBoost" in components:
            self.cpp_info.components["InfovisBoost"].requires.extend(["boost::headers", "boost::serialization"])
        if "InfovisBoostGraphAlgorithms" in components:
            self.cpp_info.components["InfovisBoostGraphAlgorithms"].requires.append("boost::headers")
        if "IOADIOS2" in components:
            self.cpp_info.components["IOADIOS2"].requires.append("adios2::adios2")
        if "IOCatalystConduit" in components:
            self.cpp_info.components["IOCatalystConduit"].requires.append("catalyst::catalyst")
        if "IOFFMPEG" in components:
            self.cpp_info.components["IOFFMPEG"].requires.extend(["ffmpeg::avformat", "ffmpeg::avcodec", "ffmpeg::avutil", "ffmpeg::swscale", "ffmpeg::swresample"])
        if "IOGDAL" in components:
            self.cpp_info.components["IOGDAL"].requires.append("gdal::gdal")
        if "IOLAS" in components:
            self.cpp_info.components["IOLAS"].requires.append("liblas::liblas")
            self.cpp_info.components["IOLAS"].requires.extend(["boost::program_options", "boost::thread", "boost::system", "boost::iostreams", "boost::filesystem"])
        if "IOMySQL" in components:
            if self.options.with_mysql == "mariadb-connector-c":
                self.cpp_info.components["IOMySQL"].requires.append("mariadb-connector-c::mariadb-connector-c")
            elif self.options.with_mysql == "libmysqlclient":
                self.cpp_info.components["IOMySQL"].requires.append("libmysqlclient::libmysqlclient")
        if "IOOCCT" in components:
            self.cpp_info.components["IOOCCT"].requires.extend(["opencascade::occt_tkstep", "opencascade::occt_tkiges", "opencascade::occt_tkmesh", "opencascade::occt_tkxdestep", "opencascade::occt_tkxdeiges"])
        if "IOODBC" in components:
            self.cpp_info.components["IOODBC"].requires.append("odbc::odbc")
        if "IOOpenVDB" in components:
            self.cpp_info.components["IOOpenVDB"].requires.append("openvdb::openvdb")
        if "IOPDAL" in components:
            self.cpp_info.components["IOPDAL"].requires.append("pdal::pdal")
        if "IOPostgreSQL" in components:
            self.cpp_info.components["IOPostgreSQL"].requires.append("libpq::libpq")
        if "RenderingLookingGlass" in components:
            self.cpp_info.components["RenderingLookingGlass"].requires.append("holoplaycore::holoplaycore")
        if "RenderingFreeTypeFontConfig" in components:
            self.cpp_info.components["RenderingFreeTypeFontConfig"].requires.append("fontconfig::fontconfig")
        if "RenderingOpenGL2" in components:
            if self.options.with_sdl2:
                self.cpp_info.components["RenderingOpenGL2"].requires.append("sdl::sdl")
            if self.options.get_safe("with_x11"):
                self.cpp_info.components["RenderingOpenGL2"].requires.extend(["xorg::x11", "xorg::xcursor"])
            if self.options.get_safe("with_cocoa"):
                self.cpp_info.components["RenderingOpenGL2"].frameworks.append("Cocoa")
            if self.options.get_safe("with_directx"):
                self.cpp_info.components["RenderingOpenGL2"].requires.extend(["directx::d3d11", "directx::dxgi"])
        if "RenderingOpenVR" in components:
            self.cpp_info.components["RenderingOpenVR"].requires.append("openvr::openvr")
        if "RenderingOpenXR" in components:
            self.cpp_info.components["RenderingOpenXR"].requires.append("openxr::openxr")
        if "RenderingOpenXRRemoting" in components:
            self.cpp_info.components["RenderingOpenXRRemoting"].requires.append("openxr::openxr")
        if "RenderingQt" in components:
            self.cpp_info.components["RenderingQt"].requires.append("qt::qtWidgets")
        if "RenderingRayTracing" in components:
            if self.options.get_safe("with_ospray"):
                self.cpp_info.components["RenderingRayTracing"].requires.append("ospray::ospray")
            if self.options.get_safe("with_openimagedenoise"):
                self.cpp_info.components["RenderingRayTracing"].requires.append("openimagedenoise::openimagedenoise")
        if "RenderingRayTracing" in components and self.options.get_safe("with_visrtx"):
            self.cpp_info.components["RenderingRayTracing"].requires.append("visrtx::visrtx")
        if "RenderingUI" in components:
            if self.options.with_sdl2:
                self.cpp_info.components["RenderingUI"].requires.append("sdl::sdl")
            if self.options.get_safe("with_x11"):
                self.cpp_info.components["RenderingUI"].requires.append("xorg::x11")
            if self.options.get_safe("with_cocoa"):
                self.cpp_info.components["RenderingUI"].frameworks.append("Cocoa")
        if "RenderingVR" in components and self.options.with_zeromq:
            self.cpp_info.components["RenderingVR"].requires.append("zeromq::zeromq")
        if "RenderingWebGPU" in components:
            self.cpp_info.components["RenderingWebGPU"].requires.append("sdl::sdl")
            if self.settings.os != "Emscripten":
                self.cpp_info.components["RenderingWebGPU"].requires.append("dawn::dawn")
        # if "RenderingZSpace" in components:
        #     self.cpp_info.components["RenderingZSpace"].requires.append("zspace::zspace")
        if "fides" in components:
            self.cpp_info.components["fides"].requires.append("adios2::adios2")
        if "xdmf3" in components:
            self.cpp_info.components["xdmf3"].requires.append("boost::headers")
        if "ViewsQt" in components:
            self.cpp_info.components["ViewsQt"].requires.append("qt::qtWidgets")

        for component_name, component in self.cpp_info.components.items():
            self.output.debug(f"COMPONENT: {component_name}")
            if component.libs:
                self.output.debug(f" - libs: {component.libs}")
            if component.defines:
                self.output.debug(f" - defines: {component.defines}")
            if component.requires:
                self.output.debug(f" - requires: {component.requires}")
            if component.system_libs:
                self.output.debug(f" - system_libs: {component.system_libs}")
            if component.frameworks:
                self.output.debug(f" - frameworks: {component.frameworks}")
