from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, get, rename, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
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

        # osgearth has support for an imgui integration, but it is honestly a mess:
        #
        #   - osgearth v3.2 includes an embedded version of imgui (and imnodes) which is used to build the imgui
        #     nodekit, but only if GLEW exists as a dependency.
        #
        #   - osgearth v3.3 removes the embedded version of imgui (and imnodes), effectively rendering the imgui nodekit
        #     unusable (that is, unless the user actually copies their own version of imgui into the source directory).
        #
        #   - osgearth v3.7.2 yet again includes an embedded version of imgui (and imnodes), and yet again, GLEW must
        #     exist as a dependency in order to build the imgui nodekit. This time, however, there is an additional
        #     requirement: the OSGEARTH_BUILD_IMGUI_NODEKIT CMake variable must also be set.
        #
        # It should be possible to patch osgearth to ensure consistency between all of our supported versions by doing
        # the following:
        #
        #   - Replace the embedded versions of imgui and imnodes with their corresponding ConanFile.requires dependency.
        #
        #   - Ensure that the OSGEARTH_BUILD_IMGUI_NODEKIT CMake variable is respected across every osgearth version.
        #
        #   - Remove the explicit dependency on GLEW. (NOTE: This would be ideal, since osgearth only ever depends on
        #     GLEW to support its embedded version of imgui. However, it probably isn't required that we do this.)
        #
        # For now, we simply disable the imgui nodekit.
        #
        # "build_imgui_nodekit": [True, False],

        "build_procedural_nodekit": [True, False],
        # "build_triton_nodekit": [True, False],
        # "build_silverlining_nodekit": [True, False],
        "build_leveldb_cache": [True, False],
        "build_rocksdb_cache": [True, False],
        "build_zip_plugin": [True, False],
        "enable_geocoder": [True, False],
        "with_geos": [True, False],
        "with_sqlite3": [True, False],
        "with_draco": [True, False],
        # "with_basisu": [True, False],
        "with_protobuf": [True, False],
        "with_webp": [True, False],
        "install_shaders": [True, False],
        "enable_nvtt_cpu_mipmaps": [True, False],
        "enable_wininet_for_http": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        # "build_imgui_nodekit": False,
        "build_procedural_nodekit": True,
        # "build_triton_nodekit": False,
        # "build_silverlining_nodekit": False,
        "build_leveldb_cache": False,
        "build_rocksdb_cache": False,
        "build_zip_plugin": True,
        "enable_geocoder": False,
        "with_geos": True,
        "with_sqlite3": True,
        "with_draco": False,
        # "with_basisu": False,
        "with_protobuf": True,
        "with_webp": True,
        "install_shaders": True,
        "enable_nvtt_cpu_mipmaps": False,
        "enable_wininet_for_http": False,
    }

    short_paths = True
    exports_sources = "CMakeLists.txt", "patches/*.patch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return (11 if Version(self.version) < "3.7.2" else 14)

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

        if is_msvc(self) and Version(self.version) < "3.7.2":
            self.options.build_procedural_nodekit = False

        if Version(self.version) < "3.7.2":
            if self.settings.compiler == "gcc" and self.settings.compiler.version == "11":
                # need draco >= 1.4.0 for gcc11
                # https://github.com/google/draco/issues/635
                self.options.rm_safe("with_draco")
        else:
            self.options.rm_safe("build_leveldb_cache")
            self.options.rm_safe("with_draco")

    def requirements(self):
        self.requires("opengl/system")
        self.requires("gdal/3.4.3")
        self.requires("openscenegraph/3.6.5", transitive_headers=True)
        self.requires("libcurl/8.12.1")
        self.requires("lerc/2.2")
        self.requires("rapidjson/1.1.0")

        # if self.options.build_triton_nodekit:
        #     self.requires("triton_nodekit")
        # if self.options.build_silverlining_nodekit:
        #     self.requires("silverlining_nodekit")

        if self.options.get_safe("build_leveldb_cache"):
            self.requires("leveldb/1.22")
        if self.options.build_rocksdb_cache:
            self.requires("rocksdb/6.29.5")
        if self.options.build_zip_plugin:
            self.requires("libzip/1.7.3")
        if self.options.with_geos:
            self.requires("geos/3.11.1")
        if self.options.with_sqlite3:
            self.requires("sqlite3/[>=3.42 <4]")
        if self.options.get_safe("with_draco"):
            self.requires("draco/1.4.3")
        # if self.options.with_basisu:
        #     self.requires("basisu")
        if self.options.with_protobuf:
            self.requires("protobuf/3.21.12")
        if self.options.with_webp:
            self.requires("libwebp/1.3.1")

    def _patch_sources(self):
        apply_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

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

        # Ideally, we would have this:
        #
        # toolchain.variables["OSGEARTH_BUILD_IMGUI_NODEKIT"] = self.options.build_imgui_nodekit
        #
        # See the comments for the (hypothetical) "build_imgui_nodekit" option for more details on why we always
        # disable this nodekit.
        if Version(self.version) >= "3.7.2":
            toolchain.variables["OSGEARTH_BUILD_IMGUI_NODEKIT"] = False

        toolchain.variables["OSGEARTH_BUILD_PROCEDURAL_NODEKIT"] = self.options.build_procedural_nodekit
        # toolchain.variables["OSGEARTH_BUILD_TRITON_NODEKIT"] = self.options.build_triton_nodekit
        # toolchain.variables["OSGEARTH_BUILD_SILVERLINING_NODEKIT"] = self.options.build_silverlining_nodekit

        if Version(self.version) < "3.7.2":
            toolchain.variables["OSGEARTH_BUILD_LEVELDB_CACHE"] = self.options.build_leveldb_cache

            # In osgEarth v3.7.2, the RocksDB plugin is always built if find_package(RocksDB QUIET) succeeds. In older
            # versions, we may need to set a CMake variable for it.
            toolchain.variables["OSGEARTH_BUILD_ROCKSDB_CACHE"] = self.options.build_rocksdb_cache

        toolchain.variables["OSGEARTH_BUILD_ZIP_PLUGIN"] = self.options.build_zip_plugin
        toolchain.variables["OSGEARTH_ENABLE_GEOCODER"] = self.options.enable_geocoder

        toolchain.variables["WITH_EXTERNAL_DUKTAPE"] = False
        toolchain.variables["WITH_EXTERNAL_TINYXML"] = False

        if Version(self.version) < "3.7.2":
            toolchain.variables["CURL_IS_STATIC"] = not self.dependencies["libcurl"].options.shared

        toolchain.variables["OSGEARTH_INSTALL_SHADERS"] = self.options.install_shaders
        toolchain.variables["OSGEARTH_ENABLE_NVTT_CPU_MIPMAPS"] = self.options.enable_nvtt_cpu_mipmaps
        toolchain.variables["OSGEARTH_ENABLE_WININET_FOR_HTTP"] = self.options.enable_wininet_for_http

        # our own defines for using in our top-level CMakeLists.txt
        toolchain.variables["OSGEARTH_WITH_GEOS"] = self.options.with_geos
        toolchain.variables["OSGEARTH_WITH_SQLITE3"] = self.options.with_sqlite3
        toolchain.variables["OSGEARTH_WITH_WEBP"] = self.options.with_webp

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
        self._patch_sources()

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self._source_subfolder)

        cmake = CMake(self)
        cmake.install()

        if self.options.install_shaders:
            relative_resources_root = ("resources" if Version(self.version) < "3.7.2" else "share")
            rename(self, os.path.join(self.package_folder, relative_resources_root), os.path.join(self.package_folder, "res"))

        if Version(self.version) < "3.7.2":
            rmdir(self, os.path.join(self.package_folder, "cmake"))

            if self.settings.os == "Linux":
                rename(self, os.path.join(self.package_folder, "lib64"), os.path.join(self.package_folder, "lib"))
        else:
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
                         }

        osgearth = setup_lib("osgEarth", required_libs)

        if not self.options.shared:
            osgearth.defines += ["OSGEARTH_LIBRARY_STATIC"]
        if self.options.with_geos:
            osgearth.requires += ["geos::geos"]
        if self.options.with_sqlite3:
            osgearth.requires += ["sqlite3::sqlite3"]
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

        if self.options.get_safe("build_leveldb_cache"):
            setup_plugin("osgearth_cache_leveldb").requires.append("leveldb::leveldb")

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

        if Version(self.version) < "3.7.2":
            setup_plugin("osgearth_mapinspector")
            setup_plugin("osgearth_monitor")

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
