import functools
import itertools
import json
import os
import re
from collections import OrderedDict
from pathlib import Path

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.files import export_conandata_patches, get, rmdir, rename, replace_in_file, load, save, copy, apply_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


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
        "want_all_modules": [True, False],  # Whether to initialize all module to WANT or NOT_WANT
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
        "debug_leaks": [True, False],
        ### future proofing ###
        "legacy_remove": [True, False],
        "legacy_silent": [True, False],
        "use_future_bool": [True, False],
        "use_future_const": [True, False],
        ### external deps ###
        "with_boost": [True, False],
        "with_cgns": [True, False],
        "with_cocoa": [True, False],
        "with_diy2": [True, False],
        "with_eigen": [True, False],
        "with_exodusII": [True, False],
        "with_expat": [True, False],
        "with_ffmpeg": [True, False],
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
        "with_kissfft": [True, False],
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
        "with_vpic": [True, False],
        "with_vtkm": [True, False],
        "with_x11": [True, False],
        "with_xdmf2": [True, False],
        "with_xdmf3": [True, False],
        "with_zeromq": [True, False],
        "with_zspace": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "want_all_modules": True,
        ### compile options ###
        "enable_logging": True,
        ### symmetric multiprocessing ###
        "smp_implementation": "STDThread",
        "smp_enable_sequential": True,
        "smp_enable_stdthread": True,
        "smp_enable_openmp": False,  # TODO: #22360
        "smp_enable_tbb": True,
        ### debugging ###
        "debug_modules": True,
        "debug_leaks": False,
        ### future proofing ###
        "legacy_remove": False,
        "legacy_silent": False,
        "use_future_bool": False,
        "use_future_const": False,
        ### external deps ###
        "with_boost": True,
        "with_cgns": False,  # FIXME: hdf5 conflict
        "with_cocoa": True,
        "with_diy2": True,
        "with_eigen": True,
        "with_exodusII": False,  # FIXME: requires netcdf
        "with_expat": True,
        "with_ffmpeg": False,
        "with_fontconfig": True,
        "with_freetype": True,
        "with_gdal": False,  # TODO #23233
        "with_gl2ps": False,  # FIXME: missing libglvnd binaries
        "with_glew": False,  # FIXME: missing libglvnd binaries
        "with_h5part": True,
        "with_hdf5": True,
        "with_holoplaycore": False,  # FIXME: requires glew
        "with_ioss": False,
        "with_jpeg": "libjpeg",
        "with_jsoncpp": True,
        "with_kissfft": False,  # Cannot unvendor by default because non-default datatype=double is required
        "with_libharu": True,
        "with_libproj": False,  # FIXME: missing binaries
        "with_libxml2": True,
        "with_metaio": True,
        "with_mpi": False,  # TODO: #18980 Should enable, since disabling this disables all parallel modules
        "with_mysql": False,  # FIXME: missing binaries
        "with_netcdf": False,  # FIXME: missing binaries
        "with_nlohmannjson": True,
        "with_octree": True,
        "with_odbc": True,
        "with_ogg": False,  # FIXME: requires theora
        "with_opencascade": False,  # very heavy
        "with_opengl": False,  # FIXME: missing libglvnd binaries
        "with_openslide": False,  # TODO: #21138
        "with_openvdb": True,
        "with_openvr": False,  # FIXME: requires glew
        "with_pdal": False,  # TODO: #21296
        "with_pegtl": True,
        "with_png": True,
        "with_postgresql": True,
        "with_qt": False,  # FIXME: too many version conflicts
        "with_sdl2": True,
        "with_sqlite": True,
        "with_theora": False,  # FIXME: missing binaries
        "with_tiff": True,
        "with_vpic": True,
        "with_vtkm": False,  # FIXME: causes issues in recipe, should unvendor
        "with_x11": False,  # FIXME: requires opengl
        "with_xdmf2": True,
        "with_xdmf3": True,
        "with_zeromq": False,
        "with_zspace": True,
    }
    # All non-third-party VTK modules are also available as options.
    # e.g. "IOGeoJSON": ["auto", "YES", "WANT", "DONT_WANT", "NO"], etc.
    # See options/<version>.json for the full list of modules.
    # Note that only YES/NO values are validated in the Conan recipe,
    # WANT/DONT_WANT are only checked in the CMake configure step.

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
        all_modules = set()
        for options_json in Path(self.recipe_folder, "options").glob("*.json"):
            modules = [m for m in json.loads(options_json.read_text())["flat_external_deps"] if m[0].isupper()]
            all_modules.update(modules)
        return sorted(all_modules)

    def init(self):
        # Skip module options support for Conan v1 because
        # self.options.update(new_options, new_defaults) is not available
        if conan_version.major != 1:
            all_modules = self._modules_from_all_versions
            new_options = {mod: ["auto", "YES", "WANT", "DONT_WANT", "NO"] for mod in all_modules}
            new_defaults = {mod: "auto" for mod in all_modules}
            self.options.update(new_options, new_defaults)

    @property
    @functools.lru_cache()
    def _module_ext_deps(self):
        return json.loads(Path(self.recipe_folder, "options", f"{self.version}.json").read_text())["flat_external_deps"]
    @property
    @functools.lru_cache()
    def _module_opt_deps(self):
        return json.loads(Path(self.recipe_folder, "options", f"{self.version}.json").read_text())["optional_external_deps"]

    @property
    @functools.lru_cache()
    def _modules(self):
        return [mod for mod in self._module_ext_deps.keys() if mod[0].isupper()]

    @property
    @functools.lru_cache()
    def _vendored_deps(self):
        return [mod for mod in self._module_ext_deps.keys() if mod[0].islower()]

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
        if conan_version.major != 1:
            for opt in set(self._modules_from_all_versions) - set(self._modules):
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
        # These are always required by CommonArchive, CommonCore, CommonMath, CommonDataModel, CommonMisc, IOCore, FiltersCore, FiltersGeneral
        self.requires("double-conversion/3.3.0")
        self.requires("exprtk/0.0.2")
        self.requires("fast_float/6.1.3")
        self.requires("libarchive/3.7.4")
        self.requires("lz4/1.9.4")
        self.requires("pugixml/1.14")
        self.requires("utfcpp/4.0.4")
        self.requires("xz_utils/[>=5.4.5 <6]")
        self.requires("zlib/[>=1.2.11 <2]")
        # Used in public vtkloguru/loguru.hpp
        self.requires("fmt/10.2.1", transitive_headers=True, transitive_libs=True)

        # kissfft is always required, only replaces the vendored version if enabled.
        # VTK mangles its symbols so not unvendoring it should still not cause conflicts.
        if self.options.with_kissfft:
            # Used in public vtkFFT.h
            self.requires("kissfft/131.1.0", transitive_headers=True, transitive_libs=True)

        # The project uses modified loguru for logging, which cannot be unvendored

        if self.options.with_boost:
            # Used in public vtkVariantBoostSerialization.h
            self.requires("boost/1.84.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_cgns:
            self.requires("cgns/4.3.0")
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
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.15.0")
        if self.options.with_freetype:
            # Used in public vtkFreeTypeTools.h
            self.requires("freetype/2.13.2", transitive_headers=True, transitive_libs=True)
        if self.options.with_gdal:
            self.requires("gdal/3.9.1")
        if self.options.with_glew:
            # Used in public vtk_glew.h
            self.requires("glew/2.2.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.1")
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
            # Used in public vtk_libxml2.h
            self.requires("libxml2/[>=2.12.5 <3]", transitive_headers=True, transitive_libs=True)
        if self.options.with_mpi:
            # Used in public vtk_mpi.h
            self.requires("openmpi/4.1.6", transitive_headers=True, transitive_libs=True)
        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.1.0")
        elif self.options.with_mysql == "mariadb-connector-c":
            self.requires("mariadb-connector-c/3.3.3")
        if self.options.with_netcdf:
            # Used in public vtkexodusII/include/exodusII.h
            is_public = bool(self.options.with_exodusII)
            self.requires("netcdf/4.8.1", transitive_headers=is_public, transitive_libs=is_public)
        if self.options.with_nlohmannjson:
            self.requires("nlohmann_json/3.11.3")
        if self.options.with_odbc:
            self.requires("odbc/2.3.11")
        if self.options.with_ogg:
            self.requires("ogg/1.3.5")
        if self.options.with_opencascade:
            self.requires("opencascade/7.6.2")
        if self.options.with_opengl:
            # Used in public vtk_glew.h
            self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_openslide:
            # Used in public vtkOpenSlideReader.h
            self.requires("openslide/4.0.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_openvdb:
            self.requires("openvdb/11.0.0")
        if self.options.with_openvr:
            # Used in public vtkOpenVRModel.h
            self.requires("openvr/1.16.8", transitive_headers=True, transitive_libs=True)
        if self.options.with_pdal:
            self.requires("pdal/2.7.2")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_postgresql:
            self.requires("libpq/15.5")
        if self.options.with_qt == "5":
            # Used in public vtkQWidgetWidget.h
            self.requires("qt/[~5.15]", transitive_headers=True, transitive_libs=True)
        elif self.options.with_qt == "6":
            # Used in public vtkQWidgetWidget.h
            self.requires("qt/[>=6.7 <7]", transitive_headers=True, transitive_libs=True)
        if self.options.with_sdl2:
            # Used in public vtkSDL2OpenGLRenderWindow.h
            self.requires("sdl/2.30.5", transitive_headers=True, transitive_libs=True)
        if self.options.with_sqlite:
            self.requires("sqlite3/3.44.2")
        if self.options.with_theora:
            self.requires("theora/1.1.1")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.get_safe("with_x11"):
            # Used in public vtkXOpenGLRenderWindow.h
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_zeromq:
            self.requires("zeromq/4.3.5")
        if self.options.smp_enable_openmp:
            # '#include <omp.h>' is used in public SMP/OpenMP/vtkSMPThreadLocalBackend.h
            # '#pragma omp' is not used in any public headers
            self.requires("openmp/system", transitive_headers=True, transitive_libs=True)
        if self.options.smp_enable_tbb:
            # Used in public SMP/TBB/vtkSMPToolsImpl.txx
            self.requires("onetbb/2021.10.0", transitive_headers=True, transitive_libs=True)

        # Not available on CCI
        # vtk-m
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

    def tool_requirements(self):
        if self.options.with_qt:
            self.tool_requires("qt/<host_version>")

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
        if self.options.with_kissfft and self.dependencies["kissfft"].options.datatype != "double":
            raise ConanInvalidConfiguration(f"{self.ref} requires kissfft/*:datatype=double")
        if self.options.with_qt and not self.dependencies["qt"].options.widgets:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt/*:widgets=True")

        # Just to check for conflicts
        self._compute_module_values()

    @property
    @functools.lru_cache()
    def _default_state(self):
        return "WANT" if self.options.want_all_modules else "DONT_WANT"

    def _initial_state(self, mod):
        state = self.options.get_safe(mod, self._default_state)
        return self._default_state if state == "auto" else state

    def _validate_modules(self):
        # Compute the set of modules available with the given set of external dependencies and
        # check that no unused dependency options are enabled.
        enabled_deps = {opt.replace("with_", "") for opt, value in self.options.items() if opt.startswith("with_") and str(value) != "False"}
        available_modules = set()
        used_deps = {"kissfft"}
        for mod, deps in self._module_ext_deps.items():
            state = self._initial_state(mod)
            deps = set(deps)
            if state != "NO":
                if enabled_deps.issuperset(deps):
                    available_modules.add(mod)
                    used_deps.update(deps)
                    opt_deps = self._module_opt_deps.get(mod, [])
                    used_deps.update(set(opt_deps) & enabled_deps)
                elif state == "YES":
                    raise ConanInvalidConfiguration(f"Module '{mod}' is missing dependencies: {', '.join(deps - enabled_deps)}")
        unused_deps = enabled_deps - used_deps
        if unused_deps:
            msg = []
            for dep in unused_deps:
                related_requires = set()
                disabled_modules = set()
                for mod, deps in self._module_ext_deps.items():
                    if dep in deps:
                        related_requires |= set(deps) - {dep}
                        if self._initial_state(mod) not in ["WANT", "YES"]:
                            disabled_modules.add(mod)
                msg.append(f"\n  - with_{dep}: also requires {', '.join(related_requires)}")
                if disabled_modules:
                    msg.append(f"; used in disabled {', '.join(disabled_modules)} modules")
            raise ConanInvalidConfiguration(f"Unused dependency options:{''.join(msg)}")
        return available_modules

    @functools.lru_cache()
    def _compute_module_values(self):
        def _yes_no(value):
            return "YES" if value else "NO"

        def _maybe(value):
            return self._default_state if value else "NO"

        if self.options.with_qt:
            qt = self.dependencies["qt"].options

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
        modules["Python"] = "NO"
        modules["GUISupportQtQuick"] = _maybe(self.options.with_qt and qt.opengl != "no" and qt.gui and qt.qtshadertools and qt.qtdeclarative)
        modules["RenderingWebGPU"] = _maybe(self.options.with_sdl2 and (self.settings.os == "Emscripten" or self.options.get_safe("with_dawn")))
        modules["cgns"] = _yes_no(self.options.with_cgns)
        modules["diy2"] = _yes_no(self.options.with_diy2)
        modules["doubleconversion"] = "YES"
        modules["eigen"] = _yes_no(self.options.with_eigen)
        modules["exodusII"] = _yes_no(self.options.with_exodusII)
        modules["expat"] = _yes_no(self.options.with_expat)
        modules["exprtk"] = "YES"
        modules["fast_float"] = "YES"
        modules["fides"] = _yes_no(self.options.get_safe("with_adios2"))
        modules["fmt"] = "YES"
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
        modules["verdict"] = "YES"
        modules["vpic"] = _yes_no(self.options.with_vpic)
        modules["vtkvtkm"] = _yes_no(self.options.with_vtkm)
        modules["xdmf2"] = _yes_no(self.options.with_xdmf2)
        modules["xdmf3"] = _yes_no(self.options.with_xdmf3 and self.options.with_boost)
        modules["zfp"] = "NO"  # not used by any modules
        modules["zlib"] = "YES"

        # Validate module options
        available_modules = self._validate_modules()
        for mod in self._modules:
            if mod not in available_modules:
                modules[mod] = "NO"
            elif mod not in modules:
                modules[mod] = self._default_state
            # Allow user to override the computed value
            user_value = self._initial_state(mod)
            if modules[mod] == self._default_state:
                modules[mod] = user_value
            # Raise if the user's value conflicts with the computed value
            elif user_value in ["YES", "NO"] and modules[mod] != user_value:
                raise ConanInvalidConfiguration(
                    f"Option '{mod}={user_value}' conflicts with value '{modules[mod]}' computed from 'with_*' options."
                )
        return modules

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.with_qt:
            VirtualBuildEnv(self).generate()
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

        tc.variables["VTK_DEBUG_LEAKS"] = self.options.debug_leaks
        tc.variables["VTK_ENABLE_CATALYST"] = self.options.get_safe("with_catalyst", False)
        tc.variables["VTK_ENABLE_LOGGING"] = self.options.enable_logging
        tc.variables["VTK_ENABLE_OSPRAY"] = self.options.get_safe("with_ospray", False)
        tc.variables["VTK_ENABLE_VR_COLLABORATION"] = self.options.with_zeromq
        tc.variables["VTK_ENABLE_WEBGPU"] = True
        tc.variables["VTK_ENABLE_WRAPPING"] = False
        tc.variables["VTK_LEGACY_REMOVE"] = self.options.legacy_remove
        tc.variables["VTK_LEGACY_SILENT"] = self.options.legacy_silent
        tc.variables["VTK_QT_VERSION"] = self.options.with_qt
        tc.variables["VTK_SMP_ENABLE_OPENMP"] = self.options.smp_enable_openmp
        tc.variables["VTK_SMP_ENABLE_SEQUENTIAL"] = self.options.smp_enable_sequential
        tc.variables["VTK_SMP_ENABLE_STDTHREAD"] = self.options.smp_enable_stdthread
        tc.variables["VTK_SMP_ENABLE_TBB"] = self.options.smp_enable_tbb
        tc.variables["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.smp_implementation
        tc.variables["VTK_USE_COCOA"] = self.options.get_safe("with_cocoa", False)
        tc.variables["VTK_USE_CUDA"] = False  # TODO
        tc.variables["VTK_USE_FUTURE_BOOL"] = self.options.use_future_bool
        tc.variables["VTK_USE_FUTURE_CONST"] = self.options.use_future_const
        tc.variables["VTK_USE_HIP"] = False  # TODO
        tc.variables["VTK_USE_KOKKOS"] = False  # TODO
        tc.variables["VTK_USE_MEMKIND"] = False
        tc.variables["VTK_USE_MPI"] = self.options.with_mpi
        tc.variables["VTK_USE_SDL2"] = self.options.with_sdl2
        tc.variables["VTK_USE_TK"] = False  # requires wrap_python
        tc.variables["VTK_USE_X"] = self.options.get_safe("with_x11", False)
        tc.variables["VTK_WRAP_JAVA"] = False
        tc.variables["VTK_WRAP_PYTHON"] = False

        # TODO
        # VTK_ENABLE_VISRTX
        # VTK_USE_OPENGL_DELAYED_LOAD
        # VTK_USE_WIN32_OPENGL
        # VTK_USE_VIDEO_FOR_WINDOWS   for video capture
        # VTK_USE_VIDEO_FOR_WINDOWS_CAPTURE   for video capture
        # VTK_USE_MICROSOFT_MEDIA_FOUNDATION   for video capture (MP4)

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

            self.output.info("Computed module values:")
            for mod, value in sorted(self._compute_module_values().items()):
                self.output.info(f"  {mod}: {value}")

        for mod, value in self._compute_module_values().items():
            tc.variables[f"VTK_MODULE_ENABLE_VTK_{mod}"] = value

        for pkg in self._vendored_deps:
            if pkg == "vtkm":
                pkg = "vtkvtkm"
            tc.variables[f"VTK_MODULE_USE_EXTERNAL_VTK_{pkg}"] = False
        tc.variables["VTK_MODULE_USE_EXTERNAL_VTK_kissfft"] = self.options.with_kissfft
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

    def _patch_kissfft(self):
        if self.options.with_kissfft:
            # Using external kissfft, fix includes
            # strict=False to cope with no_copy_source=True
            replace_in_file(self, os.path.join(self.source_folder, "Common", "Math", "vtkFFT.h"),
                            "tools/kiss_fftr.h", "kiss_fftr.h", strict=False)
            # MomentInvariants is downloaded and only available after cmake.configure()
            path = os.path.join(self.source_folder, "Remote", "MomentInvariants", "MomentInvariants", "vtkComputeMoments.cxx")
            if os.path.exists(path):
                replace_in_file(self, path, "tools/kiss_fftnd.h", "kiss_fftnd.h")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        self._patch_kissfft()
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
        return name

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
                # vtkm is the only internal dependency that does not use the VTK:: prefix
                requires = [r for r in requires if not r.startswith("vtkm::")]
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
                if "defines" not in component:
                    component["defines"] = []
                component["defines"].append(definition)
            requires, system_libs, frameworks = self._transform_link_libraries(target_info.get("link_libraries", []))
            requires += module_info.get("deps", [])
            requires = self._remove_duplicates(requires)
            if name in requires:
                # Only VTK::pugixml has this issue as of v9.3.1
                self.output.warning(f"CMake target VTK::{name} has a circular dependency on itself")
                requires.remove(name)
            if "vtkbuild" in requires:
                requires.remove("vtkbuild")
            if requires:
                component["requires"] = requires
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
            self.output.info(f"Generating autoinit headers for {implementable} with ({', '.join(all_implementers)}) implementers")
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
        missing_reqs = {
            "pugixml": ["pugixml::pugixml"],
            "CommonArchive": ["libarchive::libarchive"],
            "DomainsMicroscopy": ["openslide::openslide"],
            "GeovisGDAL": ["gdal::gdal"],
            "GUISupportQt": ["qt::qtOpenGL", "qt::qtWidgets", "qt::qtOpenGLWidgets"],
            "GUISupportQtQuick": ["qt::qtGui", "qt::qtOpenGL", "qt::qtQuick", "qt::qtQml"],
            "GUISupportQtSQL": ["qt::qtWidgets", "qt::qtSql"],
            "InfovisBoost": ["boost::headers", "boost::serialization"],
            "InfovisBoostGraphAlgorithms": ["boost::headers"],
            "IOADIOS2": ["adios2::adios2"],
            "IOCatalystConduit": ["catalyst::catalyst"],
            "IOFFMPEG": ["ffmpeg::avformat", "ffmpeg::avcodec", "ffmpeg::avutil", "ffmpeg::swscale", "ffmpeg::swresample"],
            "IOGDAL": ["gdal::gdal"],
            "IOLAS": ["liblas::liblas", "boost::program_options", "boost::thread", "boost::system", "boost::iostreams", "boost::filesystem"],
            "IOMySQL": ["mariadb-connector-c::mariadb-connector-c"] if self.options.with_mysql == "mariadb-connector-c" else ["libmysqlclient::libmysqlclient"],
            "IOOCCT": ["opencascade::occt_tkstep", "opencascade::occt_tkiges", "opencascade::occt_tkmesh", "opencascade::occt_tkxdestep", "opencascade::occt_tkxdeiges"],
            "IOODBC": ["odbc::odbc"],
            "IOOpenVDB": ["openvdb::openvdb"],
            "IOPDAL": ["pdal::pdal"],
            "IOPostgreSQL": ["libpq::libpq"],
            "RenderingLookingGlass": ["holoplaycore::holoplaycore"],
            "RenderingFreeTypeFontConfig": ["fontconfig::fontconfig"],
            "RenderingOpenVR": ["openvr::openvr"],
            "RenderingOpenXR": ["openxr::openxr"],
            "RenderingOpenXRRemoting": ["openxr::openxr"],
            "RenderingQt": ["qt::qtWidgets"],
            "RenderingVR": ["zeromq::zeromq"],
            "RenderingWebGPU": ["sdl::sdl"],
            "RenderingZSpace": ["zspace::zspace"],
            "fides": ["adios2::adios2"],
            "xdmf3": ["boost::headers"],
            "ViewsQt": ["qt::qtWidgets"],
        }
        for component, reqs in missing_reqs.items():
            if component in components:
                self.cpp_info.components[component].requires.extend(reqs)
        if self.options.smp_enable_tbb:
            self.cpp_info.components["CommonCore"].requires.append("onetbb::libtbb")
        if self.options.smp_enable_openmp:
            self.cpp_info.components["CommonCore"].requires.append("openmp::openmp")
        if self.options.get_safe("with_memkind"):
            self.cpp_info.components["CommonCore"].requires.append("memkind::memkind")
        if "RenderingRayTracing" in components:
            if self.options.get_safe("with_visrtx"):
                self.cpp_info.components["RenderingRayTracing"].requires.append("visrtx::visrtx")
            if self.options.get_safe("with_ospray"):
                self.cpp_info.components["RenderingRayTracing"].requires.append("ospray::ospray")
            if self.options.get_safe("with_openimagedenoise"):
                self.cpp_info.components["RenderingRayTracing"].requires.append("openimagedenoise::openimagedenoise")
        if "RenderingOpenGL2" in components:
            if self.options.with_sdl2:
                self.cpp_info.components["RenderingOpenGL2"].requires.append("sdl::sdl")
            if self.options.get_safe("with_x11"):
                self.cpp_info.components["RenderingOpenGL2"].requires.extend(["xorg::x11", "xorg::xcursor"])
            if self.options.get_safe("with_cocoa"):
                self.cpp_info.components["RenderingOpenGL2"].frameworks.append("Cocoa")
            if self.options.get_safe("with_directx"):
                self.cpp_info.components["RenderingOpenGL2"].requires.extend(["directx::d3d11", "directx::dxgi"])
        if "RenderingUI" in components:
            if self.options.with_sdl2:
                self.cpp_info.components["RenderingUI"].requires.append("sdl::sdl")
            if self.options.get_safe("with_x11"):
                self.cpp_info.components["RenderingUI"].requires.append("xorg::x11")
            if self.options.get_safe("with_cocoa"):
                self.cpp_info.components["RenderingUI"].frameworks.append("Cocoa")
        if "RenderingWebGPU" in components and self.settings.os != "Emscripten":
            self.cpp_info.components["RenderingWebGPU"].requires.append("dawn::dawn")

        # Add a "poison" component to prohibit the use of the "vtk::vtk" Conan target.
        # This matches the project's behavior of not providing an aggregate VTK::VTK CMake target.
        msg = "_avoid_overlinking_against_the_whole_vtk_library_"
        self.cpp_info.components[msg].system_libs = [msg]
        self.cpp_info.set_property("cmake_target_name", msg)
        self.cpp_info.set_property("pkg_config_name", msg)

        for component_name, component in self.cpp_info.components.items():
            self.output.info(f"COMPONENT: {component_name}")
            if component.libs:
                self.output.info(f" - libs: {component.libs}")
            if component.defines:
                self.output.info(f" - defines: {component.defines}")
            if component.requires:
                self.output.info(f" - requires: {component.requires}")
            if component.system_libs:
                self.output.info(f" - system_libs: {component.system_libs}")
            if component.frameworks:
                self.output.info(f" - frameworks: {component.frameworks}")
