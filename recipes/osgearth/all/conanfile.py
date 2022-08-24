from conans import ConanFile, CMake, tools
from conan.tools.files import rename
from conan.errors import ConanInvalidConfiguration
from conans.tools import os_info
import os
import functools

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
        # "with_glew": [True, False],
        "with_protobuf": [True, False],
        "with_webp": [True, False],
        "install_shaders": [True, False],
        "enable_nvtt_cpu_mipmaps": [True, False],
        "enable_wininet_for_http": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
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
        # "with_glew": True,
        "with_protobuf": True,
        "with_webp": True,
        "install_shaders": True,
        "enable_nvtt_cpu_mipmaps": False,
        "enable_wininet_for_http": False,
    }

    short_paths = True
    exports_sources = "CMakeLists.txt", "patches/*.patch"
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        elif self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("With apple-clang cppstd needs to be set, since default is not at least c++11.")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os != "Windows":
            self.options.enable_wininet_for_http = False

        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.compiler == "Visual Studio":
            self.options.build_procedural_nodekit = False

        if self.settings.compiler == "gcc" and self.settings.compiler.version == "11":
            # need draco >= 1.4.0 for gcc11
            # https://github.com/google/draco/issues/635
            self.options.with_draco = False

    def requirements(self):

        self.requires("opengl/system")
        self.requires("gdal/3.4.3")
        self.requires("openscenegraph/3.6.5")
        self.requires("libcurl/7.83.1")
        self.requires("lerc/2.2")
        self.requires("rapidjson/1.1.0")

        self.requires("zlib/1.2.12", override=True)
        self.requires("libtiff/4.3.0", override=True)
        self.requires("openssl/1.1.1l", override=True)

        # if self.options.build_triton_nodekit:
        #     self.requires("triton_nodekit")
        # if self.options.build_silverlining_nodekit:
        #     self.requires("silverlining_nodekit")
        if self.options.build_leveldb_cache:
            self.requires("leveldb/1.22")
        if self.options.build_rocksdb_cache:
            self.requires("rocksdb/6.20.3")
        if self.options.build_zip_plugin:
            self.requires("zstd/1.4.9")  # override
        if self.options.with_geos:
            self.requires("geos/3.10.2")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.38.5")
        if self.options.with_draco:
            self.requires("draco/1.4.3")
        # if self.options.with_basisu:
        #     self.requires("basisu")
        # if self.options.with_glew:
        #     self.requires("glew/2.2.0")
        if self.options.with_protobuf:
            self.requires("protobuf/3.17.1")
        if self.options.with_webp:
            self.requires("libwebp/1.2.0")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        for package in ("Draco", "GEOS", "LevelDB", "OSG", "RocksDB", "Sqlite3", "WEBP"):
            # Prefer conan's find package scripts over osgEarth's
            os.unlink(os.path.join(self._source_subfolder, "CMakeModules", "Find{}.cmake".format(package)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

        self._patch_sources()

    @functools.lru_cache(1)
    def _configured_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OSGEARTH_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["OSGEARTH_BUILD_TOOLS"] = False
        cmake.definitions["OSGEARTH_BUILD_EXAMPLES"] = False
        cmake.definitions["OSGEARTH_BUILD_TESTS"] = False

        cmake.definitions["OSGEARTH_BUILD_PROCEDURAL_NODEKIT"] = self.options.build_procedural_nodekit
        # cmake.definitions["OSGEARTH_BUILD_TRITON_NODEKIT"] = self.options.build_triton_nodekit
        # cmake.definitions["OSGEARTH_BUILD_SILVERLINING_NODEKIT"] = self.options.build_silverlining_nodekit
        cmake.definitions["OSGEARTH_BUILD_LEVELDB_CACHE"] = self.options.build_leveldb_cache
        cmake.definitions["OSGEARTH_BUILD_ROCKSDB_CACHE"] = self.options.build_rocksdb_cache
        cmake.definitions["OSGEARTH_BUILD_ZIP_PLUGIN"] = self.options.build_zip_plugin
        cmake.definitions["OSGEARTH_ENABLE_GEOCODER"] = self.options.enable_geocoder

        cmake.definitions["WITH_EXTERNAL_DUKTAPE"] = False
        cmake.definitions["WITH_EXTERNAL_TINYXML"] = False
        cmake.definitions["CURL_IS_STATIC"] = not self.options["libcurl"].shared
        cmake.definitions["CURL_INCLUDE_DIR"] = self.deps_cpp_info["libcurl"].include_paths[0]
        cmake.definitions["OSGEARTH_INSTALL_SHADERS"] = self.options.install_shaders
        cmake.definitions["OSGEARTH_ENABLE_NVTT_CPU_MIPMAPS"] = self.options.enable_nvtt_cpu_mipmaps
        cmake.definitions["OSGEARTH_ENABLE_WININET_FOR_HTTP"] = self.options.enable_wininet_for_http

        # our own defines for using in our top-level CMakeLists.txt
        cmake.definitions["OSGEARTH_WITH_GEOS"] = self.options.with_geos
        cmake.definitions["OSGEARTH_WITH_SQLITE3"] = self.options.with_sqlite3
        cmake.definitions["OSGEARTH_WITH_WEBP"] = self.options.with_webp

        cmake.configure()

        return cmake

    def build(self):
        self._configured_cmake().build()

    def package(self):
        self._configured_cmake().install()
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)

        if self.options.install_shaders:
            rename(self, os.path.join(self.package_folder, "resources"), os.path.join(self.package_folder, "res"))

        if os_info.is_linux:
            rename(self, os.path.join(self.package_folder, "lib64"), os.path.join(self.package_folder, "lib"))

        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
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
        required_libs = {"openscenegraph": ["osg", "osgUtil", "osgSim", "osgViewer", "osgText", "osgGA", "osgShadow",
                                            "OpenThreads", "osgManipulator"],
                         "libcurl": ["libcurl"],
                         "gdal": ["gdal"],
                         "opengl": ["opengl"],
                         }

        osgearth = setup_lib("osgEarth", required_libs)

        if not self.options.shared and self.settings.compiler == "Visual Studio":
            osgearth.defines += ["OSGEARTH_LIBRARY_STATIC"]
        if self.options.build_zip_plugin:
            osgearth.requires += ["zstd::zstd"]
        if self.options.with_geos:
            osgearth.requires += ["geos::geos"]
        if self.options.with_sqlite3:
            osgearth.requires += ["sqlite3::sqlite3"]
        if self.options.with_protobuf:
            osgearth.requires += ["protobuf::protobuf"]
        if self.options.with_webp:
            osgearth.requires += ["libwebp::libwebp"]

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
                                                       .format(self.deps_cpp_info["openscenegraph"].version))]
            return plugin_library

        setup_plugin("osgearth_bumpmap")
        setup_plugin("osgearth_cache_filesystem")

        if self.options.build_leveldb_cache:
            setup_plugin("osgearth_cache_leveldb").requires.append("leveldb::leveldb")

        if self.options.build_rocksdb_cache:
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
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin/osgPlugins-{}"
                                                   .format(self.deps_cpp_info["openscenegraph"].version)))
        elif self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
