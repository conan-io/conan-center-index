from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc
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
    
    def export_sources(self):
        export_conandata_patches(self)
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        self.requires("gdal/[>=3.4 <4]")
        self.requires("openscenegraph/3.6.5")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("lerc/[>=4.0.1 <5]")
        self.requires("zlib/[>=1.2.11 <2]")
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
        apply_conandata_patches(self)
        # INFO: Let Conan manage C++ standard
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 17)", "")

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
        tc.cache_variables["OSGEARTH_BUILD_ZIP_PLUGIN"] = False
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

        if not self.options.shared and is_msvc(self):
            osgearth.defines += ["OSGEARTH_LIBRARY_STATIC"]
            osgearth.requires += ["geos::geos", "sqlite3::sqlite3", "protobuf::protobuf", "libwebp::libwebp"]

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
        setup_plugin("osgearth_bumpmap")
        setup_plugin("osgearth_cache_filesystem")
        setup_plugin("osgearth_colorramp")
        setup_plugin("osgearth_detail")
        setup_plugin("earth")
        setup_plugin("osgearth_engine_rex")
        setup_plugin("osgearth_featurefilter_intersect")
        setup_plugin("osgearth_featurefilter_join")
        setup_plugin("kml")
        setup_plugin("osgearth_mapinspector")
        setup_plugin("osgearth_monitor")
        setup_plugin("osgearth_scriptengine_javascript")
        setup_plugin("osgearth_sky_gl")
        setup_plugin("osgearth_sky_simple")
        setup_plugin("template")
        setup_plugin("osgearth_terrainshader")
        setup_plugin("webp").requires.append("libwebp::libwebp")
        setup_plugin("lerc").requires.append("lerc::lerc")
        setup_plugin("osgearth_vdatum_egm2008")
        setup_plugin("osgearth_vdatum_egm84")
        setup_plugin("osgearth_vdatum_egm96")
        setup_plugin("osgearth_viewpoints")
        setup_plugin("fastdxt")

        if self.settings.os == "Windows":
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin/osgPlugins-{}"
                                                   .format(self.dependencies["openscenegraph"].ref.version)))
        elif self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
