import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, rename, replace_in_file, save
from conan.tools.microsoft import is_msvc

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
        "build_leveldb_cache": [True, False],
        "build_procedural_nodekit": [True, False],
        "build_rocksdb_cache": [True, False],
        "build_zip_plugin": [True, False],
        "enable_geocoder": [True, False],
        "enable_profiling": [True, False],
        "enable_nvtt_cpu_mipmaps": [True, False],
        "enable_wininet_for_http": [True, False],
        "install_shaders": [True, False],
        "with_basisu": [True, False],
        "with_blend2d": [True, False],
        "with_blosc": [True, False],
        "with_draco": [True, False],
        "with_duktape": [True, False],
        "with_geos": [True, False],
        "with_glew": [True, False],
        "with_protobuf": [True, False],
        "with_spdlog": [True, False],
        "with_sqlite3": [True, False],
        "with_tinyxml": [True, False],
        "with_webp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_leveldb_cache": False,
        "build_procedural_nodekit": True,
        "build_rocksdb_cache": False,
        "build_zip_plugin": True,
        "enable_geocoder": False,
        "enable_nvtt_cpu_mipmaps": False,
        "enable_profiling": False,
        "enable_wininet_for_http": False,
        "install_shaders": True,
        "with_basisu": False,
        "with_blend2d": False,
        "with_blosc": True,
        "with_draco": True,
        "with_duktape": True,
        "with_geos": True,
        "with_glew": True,
        "with_protobuf": True,
        "with_spdlog": True,
        "with_sqlite3": True,
        "with_tinyxml": False,  # fails with osgEarth::TiXmlDocument etc linker errors
        "with_webp": True,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

        if self.settings.os != "Windows":
            self.options.enable_wininet_for_http = False

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
        self.requires("gdal/3.8.0")
        self.requires("lerc/4.0.1")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libzip/1.10.1")
        self.requires("opengl/system")
        self.requires("openscenegraph/3.6.5", transitive_headers=True, transitive_libs=True)
        self.requires("rapidjson/cci.20230929")

        if self.options.build_leveldb_cache:
            self.requires("leveldb/1.23")
        if self.options.build_rocksdb_cache:
            self.requires("rocksdb/6.29.5")
        if self.options.enable_profiling:
            self.requires("tracy/0.10")
        if self.options.with_basisu:
            self.requires("libbasisu/1.14.0")  # libbasisu 1.15+ is not compatible
        if self.options.with_blend2d:
            self.requires("blend2d/0.10.6")
        if self.options.with_blosc:
            self.requires("c-blosc/1.21.5")
        if self.options.with_draco:
            self.requires("draco/1.5.6")
        if self.options.with_duktape:
            self.requires("duktape/2.7.0")
        if self.options.with_geos:
            # https://github.com/gwaldron/osgearth/blob/osgearth-3.5/src/osgEarth/GEOS#L32
            self.requires("geos/3.12.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_glew:
            self.requires("glew/2.2.0")
        if self.options.with_protobuf:
            # Used transitively by the generated headers
            self.requires("protobuf/3.21.12", transitive_headers=True, transitive_libs=True)
        if self.options.with_spdlog:
            self.requires("spdlog/1.12.0")
        if self.options.with_sqlite3:
            self.requires("sqlite3/[>=3.42 <4]")
        if self.options.with_tinyxml:
            self.requires("tinyxml/2.6.2")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")

        # TODO:
        # - Unvendor imgui
        # - Unvendor portable-file-dialogs

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OSGEARTH_SRC_DIR"] = self.source_folder.replace("\\", "/")

        tc.variables["OSGEARTH_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["OSGEARTH_BUILD_TOOLS"] = False
        tc.variables["OSGEARTH_BUILD_EXAMPLES"] = False
        tc.variables["OSGEARTH_BUILD_TESTS"] = False

        tc.variables["OSGEARTH_BUILD_PROCEDURAL_NODEKIT"] = self.options.build_procedural_nodekit
        # tc.variables["OSGEARTH_BUILD_TRITON_NODEKIT"] = self.options.build_triton_nodekit
        # tc.variables["OSGEARTH_BUILD_SILVERLINING_NODEKIT"] = self.options.build_silverlining_nodekit
        tc.variables["OSGEARTH_BUILD_LEVELDB_CACHE"] = self.options.build_leveldb_cache
        tc.variables["OSGEARTH_BUILD_ROCKSDB_CACHE"] = self.options.build_rocksdb_cache
        tc.variables["OSGEARTH_BUILD_ZIP_PLUGIN"] = self.options.build_zip_plugin
        tc.variables["OSGEARTH_ENABLE_GEOCODER"] = self.options.enable_geocoder

        tc.variables["WITH_EXTERNAL_DUKTAPE"] = False
        tc.variables["WITH_EXTERNAL_TINYXML"] = False
        tc.variables["CURL_IS_STATIC"] = not self.dependencies["libcurl"].options.shared
        tc.variables["CURL_INCLUDE_DIR"] = self.dependencies["libcurl"].cpp_info.includedir
        tc.variables["OSGEARTH_INSTALL_SHADERS"] = self.options.install_shaders
        tc.variables["OSGEARTH_ENABLE_NVTT_CPU_MIPMAPS"] = self.options.enable_nvtt_cpu_mipmaps
        tc.variables["OSGEARTH_ENABLE_WININET_FOR_HTTP"] = self.options.enable_wininet_for_http

        # our own defines for using in our top-level CMakeLists.txt
        tc.variables["WITH_BASISU"] = self.options.with_basisu
        tc.variables["WITH_BLEND2D"] = self.options.with_blend2d
        tc.variables["WITH_BLOSC"] = self.options.with_blosc
        tc.variables["WITH_DRACO"] = self.options.with_draco
        tc.variables["WITH_DUKTAPE"] = self.options.with_duktape
        tc.variables["WITH_GEOS"] = self.options.with_geos
        tc.variables["WITH_GLEW"] = self.options.with_glew
        tc.variables["WITH_PROTOBUF"] = self.options.with_protobuf
        tc.variables["WITH_SPDLOG"] = self.options.with_spdlog
        tc.variables["WITH_SQLITE3"] = self.options.with_sqlite3
        tc.variables["WITH_TINYXML"] = self.options.with_tinyxml
        tc.variables["WITH_TRACY"] = self.options.enable_profiling
        tc.variables["WITH_WEBP"] = self.options.with_webp
        tc.generate()

        # tinygltf uses rapidjson headers without a directory prefix
        self.dependencies["rapidjson"].cpp_info.includedirs.append(
            os.path.join(self.dependencies["rapidjson"].package_folder, "include", "rapidjson")
        )

        deps = CMakeDeps(self)
        for package, cmake_file_name in self._cmake_dependency_names.items():
            deps.set_property(package, "cmake_file_name", cmake_file_name)
        deps.set_property("rapidjson", "cmake_target_name", "rapidjson::rapidjson")
        deps.generate()

    @property
    def _cmake_dependency_names(self):
        return {
            "blend2d": "Blend2D",
            "c-blosc": "Blosc",
            "draco": "Draco",
            "duktape": "Duktape",
            "geos": "GEOS",
            "glew": "GLEW",
            "leveldb": "LevelDB",
            "libbasisu": "BASISU",
            "libwebp": "WEBP",
            "libzip": "LibZip",
            "openscenegraph": "OSG",
            "protobuf": "Protobuf",
            "spdlog": "spdlog",
            "sqlite3": "Sqlite3",
            "tinyxml": "TinyXML",
            "tracy": "Tracy",
            # TODO:
            # "CesiumNative",
            # "GLCORE",
            # "OpenGLES",
            # "OpenThreads",
            # "SilverLining",
            # "Triton",
        }

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Replace custom FindXXX.cmake modules with Conan-provided ones
        for package in self._cmake_dependency_names.values():
            module_file = os.path.join(self.source_folder, "CMakeModules", f"Find{package}.cmake")
            if os.path.isfile(module_file):
                os.unlink(module_file)
        # Handle changed source root
        for file in sorted(self.source_path.rglob("CMakeLists.txt")) + sorted(self.source_path.rglob("*.cmake")):
            content = file.read_text(encoding="utf8")
            if "CMAKE_SOURCE_DIR" in content:
                file.write_text(content.replace("${CMAKE_SOURCE_DIR}/", "${CMAKE_SOURCE_DIR}/src/"), encoding="utf8")
        # Unvendor lerc
        rmdir(self, os.path.join(self.source_folder, "src", "third_party", "lerc"))
        save(self, os.path.join(self.source_folder, "src", "osgEarthDrivers", "lerc", "CMakeLists.txt"),
             "SET(TARGET_LIBRARIES_VARS OSG_LIBRARY OSGDB_LIBRARY OPENTHREADS_LIBRARY lerc_LIBRARIES)\n"
             "SET(TARGET_SRC ReaderWriterLERC.cpp)\n"
             "SETUP_PLUGIN(lerc)\n")
        # Unvendor rapidjson (but not tinygltf as osgEarth uses a modified version)
        rmdir(self, os.path.join(self.source_folder, "src", "third_party", "rapidjson"))
        replace_in_file(self, os.path.join(self.source_folder, "src", "osgEarthDrivers", "gltf", "CMakeLists.txt"),
                        "${OSGEARTH_EMBEDDED_THIRD_PARTY_DIR}/rapidjson/include/rapidjson", "")
        replace_in_file(self, os.path.join(self.source_folder, "src", "osgEarthDrivers", "gltf", "CMakeLists.txt"),
                        "SET(TARGET_LIBRARIES_VARS ", "SET(TARGET_LIBRARIES_VARS RapidJSON_LIBRARIES ")
        # Allow find_package() to be called only from the CMakelists.txt in the recipe
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "find_package", "# find_package")
        # Fix libbasisu include
        replace_in_file(self, os.path.join(self.source_folder, "src", "osgEarthDrivers", "basis", "ReaderWriterBasis.cpp"),
                        "#include <basisu/", "#include <libbasisu/")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        if self.options.install_shaders:
            rename(self, os.path.join(self.package_folder, "resources"), os.path.join(self.package_folder, "res"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            rename(self, os.path.join(self.package_folder, "lib64"), os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "cmake"))

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
            osg_version = self.dependencies["openscenegraph"].ref.version
            self.env_info.PATH.append(os.path.join(self.package_folder, os.path.join("bin", f"osgPlugins-{osg_version}")))
            self.runenv_info.append_path("PATH", os.path.join(self.package_folder, os.path.join("bin", f"osgPlugins-{osg_version}")))
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
