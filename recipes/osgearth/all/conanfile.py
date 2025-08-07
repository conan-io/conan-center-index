from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, get, rename, rmdir
import os

required_conan_version = ">=1.33.0"

class OsgearthConan(ConanFile):
    name = "osgearth"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "osgEarth is a C++ geospatial SDK and terrain engine. \
                   Just create a simple XML file, point it at your map data, \
                   and go! osgEarth supports all kinds of data and comes with \
                   lots of examples to help you get up and running quickly \
                   and easily."
    topics = "openscenegraph", "graphics"
    settings = "os", "compiler", "build_type", "arch"
    homepage = "http://osgearth.org/"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_procedural_nodekit": [True, False],
        "build_rocksdb_cache": [True, False],
        "build_zip_plugin": [True, False],
        "enable_geocoder": [True, False],
        "with_geos": [True, False],
        "with_protobuf": [True, False],
        "with_webp": [True, False],
        "install_shaders": [True, False],
        "enable_wininet_for_http": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "build_procedural_nodekit": True,
        "build_rocksdb_cache": False,
        "build_zip_plugin": True,
        "enable_geocoder": False,
        "with_geos": True,
        "with_protobuf": True,
        "with_webp": True,
        "install_shaders": True,
        "enable_wininet_for_http": False,
    }

    short_paths = True
    exports_sources = "patches/*.patch"

    @property
    def _minimum_cpp_standard(self):
        return 14

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        # The official Conan recipe for rocksdb will delete all of the C++ headers from the packaged include directory
        # in a shared build. osgearth assumes that these headers are available, however. What this means is that we
        # cannot currently support shared builds of rocksdb.
        if self.options.build_rocksdb_cache:
            is_rocksdb_shared = self.dependencies["rocksdb"].options.shared

            if is_rocksdb_shared:
                raise ConanInvalidConfiguration('The "build_rocksdb_cache" option cannot be used with a shared build of rocksdb.')

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def config_options(self):
        if self.settings.os != "Windows":
            self.options.enable_wininet_for_http = False

        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("opengl/system")
        self.requires("gdal/3.4.3")
        self.requires("openscenegraph/3.6.5", transitive_headers=True)
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("lerc/2.2")
        self.requires("rapidjson/1.1.0")
        self.requires("sqlite3/[>=3.42 <4]")

        if self.options.build_rocksdb_cache:
            self.requires("rocksdb/6.29.5")
        if self.options.build_zip_plugin:
            self.requires("libzip/1.7.3")
        if self.options.with_geos:
            self.requires("geos/3.11.1")
        if self.options.with_protobuf:
            self.requires("protobuf/3.21.12")
        if self.options.with_webp:
            self.requires("libwebp/[>=1.3.2 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def _get_library_postfix(self, build_type: str) -> str:
        # We want our library postfix (that is, the value of the CMAKE_*_POSTFIX CMake variable for
        # self.settings.build_type) to be set to match the definition of the OSG_LIBRARY_POSTFIX preprocessor macro in
        # openscenegraph::osgDB. This macro is only defined in a shared build of openscenegraph.
        #
        # We do this because osgDB implicitly expects each loaded plugin to include a postfix matching the value of
        # OSG_LIBRARY_POSTFIX in its file name.

        is_osg_shared = self.dependencies["openscenegraph"].options.shared

        if not is_osg_shared:
            return ""

        # The OSG_LIBRARY_POSTFIX preprocessor macro is set to match the value of the CMAKE_*_POSTFIX CMake variable for
        # a given build type. The CMake scripts for openscenegraph set these variables as follows:
        library_postfix_dict = {
            "Debug": "d",
            "Release": "",
            "RelWithDebInfo": "rd",
            "MinSizeRel": "s"
        }

        if build_type not in library_postfix_dict:
            return ""

        return library_postfix_dict[build_type]

    def generate(self):
        toolchain = CMakeToolchain(self)

        toolchain.variables["OSGEARTH_BUILD_SHARED_LIBS"] = self.options.shared
        toolchain.variables["OSGEARTH_BUILD_TOOLS"] = False
        toolchain.variables["OSGEARTH_BUILD_EXAMPLES"] = False
        toolchain.variables["OSGEARTH_BUILD_TESTS"] = False

        # Several of the optional osgearth nodekits are currently unsupported by this recipe, and are always
        # disabled.
        toolchain.variables["OSGEARTH_BUILD_CESIUM_NODEKIT"] = False
        toolchain.variables["OSGEARTH_BUILD_IMGUI_NODEKIT"] = False
        toolchain.variables["OSGEARTH_BUILD_PROCEDURAL_NODEKIT"] = self.options.build_procedural_nodekit
        toolchain.variables["OSGEARTH_BUILD_SILVERLINING_NODEKIT"] = False
        toolchain.variables["OSGEARTH_BUILD_TRITON_NODEKIT"] = False

        # In osgearth v3.7.2, the following plugins do not have a specific CMake variable:
        #
        #   - osgdb_osgearth_cache_rocksdb (find_package(RocksDB QUIET))
        #   - osgdb_webp (find_package(WebP QUIET))
        #
        # Instead, they are always built if their corresponding find_package(...) command call succeeds.

        toolchain.variables["OSGEARTH_BUILD_ZIP_PLUGIN"] = self.options.build_zip_plugin
        toolchain.variables["OSGEARTH_ENABLE_GEOCODER"] = self.options.enable_geocoder

        toolchain.variables["WITH_EXTERNAL_DUKTAPE"] = False
        toolchain.variables["WITH_EXTERNAL_TINYXML"] = False

        toolchain.variables["OSGEARTH_INSTALL_SHADERS"] = self.options.install_shaders
        toolchain.variables["OSGEARTH_ENABLE_WININET_FOR_HTTP"] = self.options.enable_wininet_for_http

        # Set the CMAKE_*_POSTFIX variables in the CMake cache here for consistency. There are some oddities with how
        # osgearth typically defines these, especially when compared to the defaults used by OpenSceneGraph.
        toolchain.variables["CMAKE_DEBUG_POSTFIX"] = self._get_library_postfix("Debug")
        toolchain.variables["CMAKE_RELEASE_POSTFIX"] = self._get_library_postfix("Release")
        toolchain.variables["CMAKE_MINSIZEREL_POSTFIX"] = self._get_library_postfix("MinSizeRel")
        toolchain.variables["CMAKE_RELWITHDEBINFO_POSTFIX"] = self._get_library_postfix("RelWithDebInfo")

        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        if self.options.install_shaders:
            rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        postfix = self._get_library_postfix(str(self.settings.build_type))

        def setup_lib(library, required_components):
            lib = self.cpp_info.components[library]
            lib.libs = [library + postfix]

            for source_lib, components in required_components.items():
                lib.requires += [source_lib + "::" + comp for comp in components]

            return lib

        # osgEarth the main lib
        required_libs = {"openscenegraph": ["osg", "osgUtil", "osgSim", "osgViewer", "osgText", "osgGA", "osgShadow",
                                            "OpenThreads", "osgManipulator"],
                         "libcurl": ["libcurl"],
                         "gdal": ["gdal"],
                         "opengl": ["opengl"],
                         "sqlite3": ["sqlite3"]
                         }

        osgearth = setup_lib("osgEarth", required_libs)

        if not self.options.shared:
            osgearth.defines += ["OSGEARTH_LIBRARY_STATIC"]
        if self.options.with_geos:
            osgearth.requires += ["geos::geos"]
        if self.options.with_protobuf:
            osgearth.requires += ["protobuf::protobuf"]

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
                plugin_library.libdirs = [os.path.join("lib", "osgPlugins-{}"
                                                       .format(self.dependencies["openscenegraph"].ref.version))]
            return plugin_library

        setup_plugin("osgearth_bumpmap")
        setup_plugin("osgearth_cache_filesystem")

        if self.options.build_rocksdb_cache:
            setup_plugin("osgearth_cache_rocksdb").requires.append("rocksdb::rocksdb")

        setup_plugin("osgearth_colorramp")
        setup_plugin("osgearth_detail")
        setup_plugin("earth")
        setup_plugin("osgearth_engine_rex")
        setup_plugin("fastdxt")
        setup_plugin("osgearth_featurefilter_intersect")
        setup_plugin("osgearth_featurefilter_join")
        setup_plugin("gltf").requires.append("rapidjson::rapidjson")
        setup_plugin("kml")
        setup_plugin("lerc").requires.append("lerc::lerc")
        setup_plugin("osgearth_scriptengine_javascript")
        setup_plugin("osgearth_sky_gl")
        setup_plugin("osgearth_sky_simple")
        setup_plugin("template")
        setup_plugin("osgearth_terrainshader")
        setup_plugin("osgearth_vdatum_egm2008")
        setup_plugin("osgearth_vdatum_egm84")
        setup_plugin("osgearth_vdatum_egm96")
        setup_plugin("osgearth_viewpoints")

        if self.options.with_webp:
            setup_plugin("webp").requires.append("libwebp::libwebp")

        if self.options.build_zip_plugin:
            setup_plugin("zip").requires.append("libzip::_libzip")

        if self.settings.os == "Windows":
            self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))
            self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin/osgPlugins-{}"
                                                              .format(self.dependencies["openscenegraph"].ref.version)))
        elif self.settings.os == "Linux":
            self.runenv_info.append_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib"))
