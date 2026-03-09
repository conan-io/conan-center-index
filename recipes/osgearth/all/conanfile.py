from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.1"

class OsgearthConan(ConanFile):
    name = "osgearth"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "3D Maps & Terrain SDK (C++)"    
    topics = "openscenegraph", "opengl", "3d", "maps", "terrain"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    homepage = "https://www.pelicanmapping.com/home-1/opensource"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],        
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        self.requires("gdal/[>=3.4 <4]")
        self.requires("openscenegraph/3.6.5")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("lerc/[>=4.0.1 <5]")
        # self.requires("rapidjson/cci.20250205")
        self.requires("zlib/[>=1.2.11 <2]")
        # self.requires("libtiff/[>=4.6.0 <5]")
        # self.requires("libpng/[>=1.6 <2]")
        self.requires("protobuf/[>=5.27.0 <7]")
        self.requires("geos/[>=3.12.0 <4]")
        self.requires("sqlite3/[>=3.42 <4]")
        self.requires("draco/1.5.7")
        self.requires("libwebp/[>=1.4.0 <2]")
        self.requires("spdlog/[>=1.11 <2]")
        
    def validate(self):
        check_min_cppstd(self, 17)
        
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # INFO: Let Conan manage C++ standard
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 17)", "")
        # INFO: Manage lerc dependency
        lerc_cmake = os.path.join(self.source_folder, "src", "osgEarthDrivers", "lerc", "CMakeLists.txt")
        replace_in_file(self, lerc_cmake, "include_directories", "find_package(lerc REQUIRED)\nadd_osgearth_plugin(TARGET osgdb_lerc SOURCES ReaderWriterLERC.cpp LIBRARIES PRIVATE lerc::lerc)\nreturn()\ninclude_directories")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OSGEARTH_BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["OSGEARTH_BUILD_TOOLS"] = False
        tc.cache_variables["OSGEARTH_BUILD_EXAMPLES"] = False
        tc.cache_variables["OSGEARTH_BUILD_TESTS"] = False
        tc.cache_variables["OSGEARTH_BUILD_DOCS"] = False

        tc.cache_variables["OSGEARTH_BUILD_PROCEDURAL_NODEKIT"] = False
        tc.cache_variables["OSGEARTH_BUILD_TRITON_NODEKIT"] = False
        tc.cache_variables["OSGEARTH_BUILD_SILVERLINING_NODEKIT"] = False
        # tc.cache_variables["OSGEARTH_BUILD_LEVELDB_CACHE"] = self.options.build_leveldb_cache
        # tc.cache_variables["OSGEARTH_BUILD_ROCKSDB_CACHE"] = self.options.build_rocksdb_cache
        tc.cache_variables["OSGEARTH_BUILD_ZIP_PLUGIN"] = False
        # tc.cache_variables["OSGEARTH_ENABLE_GEOCODER"] = self.options.enable_geocoder

        # tc.cache_variables["CURL_IS_STATIC"] = not self.dependencies["libcurl"].options.shared
        # tc.cache_variables["CURL_INCLUDE_DIR"] = self.dependencies["libcurl"].cpp_info.includedirs[0]
        # tc.cache_variables["OSGEARTH_INSTALL_SHADERS"] = self.options.install_shaders
        # tc.cache_variables["OSGEARTH_ENABLE_NVTT_CPU_MIPMAPS"] = self.options.enable_nvtt_cpu_mipmaps
        # tc.cache_variables["OSGEARTH_ENABLE_WININET_FOR_HTTP"] = self.options.enable_wininet_for_http

        # our own defines for using in our top-level CMakeLists.txt
        # tc.cache_variables["OSGEARTH_WITH_GEOS"] = self.options.with_geos
        # tc.cache_variables["OSGEARTH_WITH_SQLITE3"] = self.options.with_sqlite3
        # tc.cache_variables["OSGEARTH_WITH_WEBP"] = self.options.with_webp
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

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
