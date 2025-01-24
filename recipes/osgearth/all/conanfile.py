import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, rename
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class OsgearthConan(ConanFile):
    name = "osgearth"
    description = ("osgEarth is a C++ geospatial SDK and terrain engine. Just create a simple XML file, "
                   "point it at your map data, and go! osgEarth supports all kinds of data and comes with "
                   "lots of examples to help you get up and running quickly and easily.")
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://osgearth.org/"
    topics = ("openscenegraph", "graphics")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tools": [True, False],
        "build_procedural_nodekit": [True, False],
        "build_zip_plugin": [True, False],
        "enable_geocoder": [True, False],
        "install_shaders": [True, False],
        "with_basisu": [True, False],
        "with_blend2d": [True, False],
        "with_blosc": [True, False],
        "with_draco": [True, False],
        "with_duktape": [True, False],
        "with_geos": [True, False],
        "with_imgui": [True, False],
        "with_protobuf": [True, False],
        "with_rocksdb": [True, False],
        "with_spdlog": [True, False],
        "with_sqlite3": [True, False],
        "with_tinyxml": [True, False],
        "with_webp": [True, False],
        "enable_profiling": [True, False],
        "assume_single_gl_context": [True, False],
        "assume_single_threaded_osg": [True, False],
        "build_legacy_controls_api": [True, False],
        "build_legacy_splat_nodekit": [True, False],
        "enable_wininet_for_http": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_tools": False,
        "build_procedural_nodekit": False,
        "build_zip_plugin": True,
        "enable_geocoder": False,
        "install_shaders": True,
        "with_basisu": True,
        "with_blend2d": True,
        "with_blosc": True,
        "with_draco": True,
        "with_duktape": True,
        "with_geos": True,
        "with_imgui": True,
        "with_protobuf": True,
        "with_rocksdb": True,
        "with_spdlog": True,
        "with_sqlite3": True,
        "with_tinyxml": True,
        "with_webp": True,
        "enable_profiling": False,
        "assume_single_gl_context": False,
        "assume_single_threaded_osg": False,
        "build_legacy_controls_api": False,
        "build_legacy_splat_nodekit": False,
        "enable_wininet_for_http": False,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

        if self.settings.os != "Windows":
            del self.options.enable_wininet_for_http

        if is_msvc(self):
            self.options.build_procedural_nodekit = False

        if self.settings.compiler == "gcc" and self.settings.compiler.version == "11":
            # need draco >= 1.4.0 for gcc11
            # https://github.com/google/draco/issues/635
            self.options.with_draco = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gdal/3.8.3")
        self.requires("glew/2.2.0")
        self.requires("imgui/1.90.9")
        self.requires("lerc/4.0.1")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libzip/1.10.1")
        self.requires("opengl/system")
        self.requires("openscenegraph/3.6.5", transitive_headers=True, transitive_libs=True)
        self.requires("rapidjson/cci.20230929")

        # Cannot unvendor tinygltf because of modifications to it:
        # https://github.com/gwaldron/osgearth/commit/dae4c9115d80eb3e655496471bbe8cdd5d6a9969

        if self.options.enable_profiling:
            self.requires("tracy/0.10")
        if self.options.with_basisu:
            self.requires("libbasisu/1.15.0")
        if self.options.with_blend2d:
            # v0.10+ is not compatible as of v3.7
            self.requires("blend2d/0.9")
        if self.options.with_blosc:
            self.requires("c-blosc/1.21.5")
        if self.options.with_draco:
            self.requires("draco/1.5.6")
        if self.options.with_duktape:
            self.requires("duktape/2.7.0")
        if self.options.with_geos:
            # https://github.com/gwaldron/osgearth/blob/osgearth-3.6/src/osgEarth/GEOS#L32
            self.requires("geos/3.12.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_imgui:
            self.requires("glew/2.2.0")
            # TODO: unvendor
            # self.requires("imgui/1.90.2")
            # self.requires("portable-file-dialogs/cci.20221111")
        if self.options.with_protobuf:
            # Used transitively by the generated headers
            self.requires("protobuf/5.27.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_rocksdb:
            self.requires("rocksdb/9.5.2")
        if self.options.with_spdlog:
            self.requires("spdlog/1.14.1")
        if self.options.with_sqlite3:
            self.requires("sqlite3/[>=3.42 <4]")
        if self.options.with_tinyxml:
            self.requires("tinyxml/2.6.2")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")

        self.requires("libpng/[>=1.6 <2]", override=True)
        self.requires("expat/[>=2.6.2 <3]", override=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")
        if self.options.with_protobuf:
            self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OSGEARTH_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["OSGEARTH_BUILD_DOCS"] = False
        tc.variables["OSGEARTH_BUILD_TESTS"] = False
        tc.variables["OSGEARTH_BUILD_EXAMPLES"] = True
        tc.variables["OSGEARTH_INSTALL_PDBS"] = False
        tc.variables["OSGEARTH_SONAMES"] = True
        tc.variables["OSGEARTH_ENABLE_FASTDXT"] = self.settings.arch in ["x86", "x86_64"]  # Requires SSE support
        tc.variables["OSGEARTH_ENABLE_PROFILING"] = self.options.enable_profiling
        tc.variables["OSGEARTH_ENABLE_WININET_FOR_HTTP"] = self.options.get_safe("enable_wininet_for_http", False)
        tc.variables["OSGEARTH_BUILD_TOOLS"] = self.options.build_tools
        tc.variables["OSGEARTH_BUILD_CESIUM_NODEKIT"] = False
        tc.variables["OSGEARTH_BUILD_IMGUI_NODEKIT"] = self.options.with_imgui
        tc.variables["OSGEARTH_BUILD_TRITON_NODEKIT"] = False
        tc.variables["OSGEARTH_BUILD_SILVERLINING_NODEKIT"] = False
        tc.variables["OSGEARTH_ENABLE_GEOCODER"] = self.options.enable_geocoder
        tc.variables["OSGEARTH_BUILD_PROCEDURAL_NODEKIT"] = self.options.build_procedural_nodekit
        tc.variables["OSGEARTH_BUILD_LEGACY_SPLAT_NODEKIT"] = self.options.build_legacy_splat_nodekit
        tc.variables["OSGEARTH_BUILD_LEGACY_CONTROLS_API"] = self.options.build_legacy_controls_api
        tc.variables["OSGEARTH_BUILD_ZIP_PLUGIN"] = self.options.build_zip_plugin
        tc.variables["OSGEARTH_ASSUME_SINGLE_GL_CONTEXT"] = self.options.assume_single_gl_context
        tc.variables["OSGEARTH_ASSUME_SINGLE_THREADED_OSG"] = self.options.assume_single_threaded_osg
        tc.variables["OSGEARTH_INSTALL_SHADERS"] = self.options.install_shaders
        tc.generate()

        deps = CMakeDeps(self)
        # Use the same name for shared and static targets
        deps.set_property("rocksdb", "cmake_target_aliases", ["RocksDB::rocksdb", "RocksDB::rocksdb-shared"])
        deps.generate()

        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.options.install_shaders:
            os.rename(os.path.join(self.package_folder, "share"),
                      os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "osgEarth")
        self.cpp_info.set_property("cmake_target_name", "osgEarth::osgEarth")

        if self.settings.build_type == "Debug":
            postfix = "d"
        elif self.settings.build_type == "RelWithDebInfo":
            postfix = "rd"
        elif self.settings.build_type == "MinSizeRel":
            postfix = "s"
        else:
            postfix = ""

        def setup_lib(library, required_components):
            lib = self.cpp_info.components[library]
            lib.libs = [library + postfix]

            for source_lib, components in required_components.items():
                lib.requires += [source_lib + "::" + comp for comp in components]

            return lib

        # osgEarth the main lib
        required_libs = {
            "openscenegraph": ["osg", "osgUtil", "osgSim", "osgViewer", "osgText", "osgGA", "osgShadow", "OpenThreads", "osgManipulator"],
            "libcurl": ["libcurl"],
            "gdal": ["gdal"],
            "opengl": ["opengl"],
            "libzip": ["libzip"],
        }

        osgearth = setup_lib("osgEarth", required_libs)

        if not self.options.shared and is_msvc(self):
            osgearth.defines += ["OSGEARTH_LIBRARY_STATIC"]

        optional_libs = {
            "enable_profiling": "tracy::tracy",
            "with_basisu": "libbasisu::libbasisu",
            "with_blend2d": "blend2d::blend2d",
            "with_blosc": "c-blosc::c-blosc",
            "with_draco": "draco::draco",
            "with_duktape": "duktape::duktape",
            "with_geos": "geos::geos",
            "with_glew": "glew::glew",
            "with_protobuf": "protobuf::protobuf",
            "with_spdlog": "spdlog::spdlog",
            "with_sqlite3": "sqlite3::sqlite3",
            "with_tinyxml": "tinyxml::tinyxml",
            "with_webp": "libwebp::libwebp",
        }
        for opt, lib in optional_libs.items():
            if getattr(self.options, opt):
                osgearth.requires.append(lib)

        # osgEarthProcedural
        if self.options.build_procedural_nodekit:
            setup_lib("osgEarthProcedural", {}).requires.append("osgEarth")

        # plugins
        def setup_plugin(plugin):
            libname = "osgdb_" + plugin
            plugin_library = self.cpp_info.components[libname]
            plugin_library.libs = [] if self.options.shared else [libname + postfix]
            plugin_library.requires = ["osgEarth"]
            if not self.options.shared:
                osg_version = self.dependencies["openscenegraph"].ref.version
                plugin_library.libdirs = [os.path.join("lib", f"osgPlugins-{osg_version}")]
            return plugin_library

        setup_plugin("osgearth_bumpmap")
        setup_plugin("osgearth_cache_filesystem")

        if self.options.build_leveldb_cache:
            setup_plugin("osgearth_cache_leveldb").requires.append("leveldb::leveldb")

        if self.options.with_rocksdb:
            setup_plugin("osgearth_cache_rocksdb").requires.append("rocksdb::rocksdb")

        setup_plugin("osgearth_bumpmap")
        setup_plugin("osgearth_cache_filesystem")
        setup_plugin("osgearth_colorramp")
        setup_plugin("osgearth_detail")
        setup_plugin("earth")
        setup_plugin("osgearth_engine_rex")
        setup_plugin("osgearth_featurefilter_intersect")
        setup_plugin("osgearth_featurefilter_join")
        setup_plugin("gltf").requires.append("rapidjson::rapidjson")
        setup_plugin("kml")
        setup_plugin("osgearth_mapinspector")
        setup_plugin("osgearth_monitor")
        setup_plugin("osgearth_scriptengine_javascript")
        setup_plugin("osgearth_sky_gl")
        setup_plugin("osgearth_sky_simple")
        setup_plugin("template")
        setup_plugin("osgearth_terrainshader")

        if self.options.with_webp:
            setup_plugin("webp").requires.append("libwebp::libwebp")

        setup_plugin("lerc").requires.append("lerc::lerc")
        setup_plugin("osgearth_vdatum_egm2008")
        setup_plugin("osgearth_vdatum_egm84")
        setup_plugin("osgearth_vdatum_egm96")
        setup_plugin("osgearth_viewpoints")
        setup_plugin("fastdxt")

        if self.settings.os == "Windows":
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
            osg_version = self.dependencies["openscenegraph"].ref.version
            self.env_info.PATH.append(os.path.join(self.package_folder, os.path.join("bin", f"osgPlugins-{osg_version}")))
            self.runenv_info.append_path("PATH", os.path.join(self.package_folder, os.path.join("bin", f"osgPlugins-{osg_version}")))
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
