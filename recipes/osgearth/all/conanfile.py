from collections.abc import Set

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
        copy(self, "conan_project_include.cmake", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"))
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        self.requires("gdal/[>=3.4 <4]")
        self.requires("openscenegraph/3.6.5")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("lerc/[>=4.0.1 <5]")
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
        # /tmp/tmp.9gUjnpfsNQ/osgearth-osgearth-3.8/src/osgEarthDrivers/gltf/CMakeLists.txt

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_OSGEARTH_INCLUDE"] = os.path.join(self.source_folder, "conan_project_include.cmake")
        tc.cache_variables["OSGEARTH_BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["OSGEARTH_BUILD_TOOLS"] = False
        tc.cache_variables["OSGEARTH_BUILD_EXAMPLES"] = False
        tc.cache_variables["OSGEARTH_BUILD_TESTS"] = False
        tc.cache_variables["OSGEARTH_BUILD_DOCS"] = False
        tc.cache_variables["OSGEARTH_BUILD_PROCEDURAL_NODEKIT"] = False
        tc.cache_variables["OSGEARTH_BUILD_TRITON_NODEKIT"] = False
        tc.cache_variables["OSGEARTH_BUILD_SILVERLINING_NODEKIT"] = False
        tc.cache_variables["OSGEARTH_BUILD_ZIP_PLUGIN"] = False
        tc.cache_variables["OSGEARTH_INSTALL_SHADERS"] = False
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
        libsuffix = {"Debug": "d", "RelWithDebInfo": "rd", "MinSizeRel": "s"}.get(str(self.settings.build_type), "")
        openscenegraph_version = self.dependencies["openscenegraph"].ref.version
        self.cpp_info.components["osgEarth"].libs = ["osgEarth" + libsuffix]
        self.cpp_info.components["osgEarth"].set_property("cmake_target_name", "osgEarth::osgEarth")
        self.cpp_info.components["osgEarth"].requires = ["openscenegraph::osg", "openscenegraph::osgUtil", "openscenegraph::osgSim",
                                                         "openscenegraph::osgViewer", "openscenegraph::osgText", "openscenegraph::osgGA",
                                                         "openscenegraph::osgShadow", "openscenegraph::OpenThreads", "openscenegraph::osgManipulator",
                                                         "libcurl::libcurl", "gdal::gdal", "opengl::opengl", "geos::geos", "sqlite3::sqlite3",
                                                         "protobuf::protobuf", "spdlog::spdlog"]
        if not self.options.shared and is_msvc(self):
            self.cpp_info.components["osgEarth"].defines.append("OSGEARTH_LIBRARY_STATIC")

        # Enabled by default via CMake OSGEARTH_BUILD_IMGUI_NODEKIT
        self.cpp_info.components["osgEarthImGui"].libs = ["osgdb_osgEarthImGui" + libsuffix]
        self.cpp_info.components["osgEarthImGui"].set_property("cmake_target_name", "osgEarth::osgEarthImGui")
        self.cpp_info.components["osgEarthImGui"].requires = ["osgEarth", "opengl::opengl"]

        # osgEarth Plugins
        self.cpp_info.components["osgdb_osgearth_bumpmap"].libs = ["osgdb_bumpmap" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_bumpmap"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_bumpmap"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_cache_filesystem"].libs = ["osgdb_osgearth_cache_filesystem" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_cache_filesystem"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_cache_filesystem"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_colorramp"].libs = ["osgdb_osgearth_colorramp" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_colorramp"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_colorramp"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_detail"].libs = ["osgdb_osgearth_detail" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_detail"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_detail"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_detail"].libs = ["osgdb_osgearth_detail" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_detail"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_detail"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_earth"].libs = ["osgdb_earth" + libsuffix]
        self.cpp_info.components["osgdb_earth"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_earth"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_engine_rex"].libs = ["osgdb_osgearth_engine_rex" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_engine_rex"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_engine_rex"].requires = ["osgEarth", "opengl::opengl"]

        self.cpp_info.components["osgdb_osgearth_featurefilter_intersect"].libs = ["osgdb_osgearth_featurefilter_intersect" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_featurefilter_intersect"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_featurefilter_intersect"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_featurefilter_join"].libs = ["osgdb_osgearth_featurefilter_join" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_featurefilter_join"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_featurefilter_join"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_kml"].libs = ["osgdb_kml" + libsuffix]
        self.cpp_info.components["osgdb_kml"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_kml"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_sky_gl"].libs = ["osgdb_osgearth_sky_gl" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_sky_gl"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_sky_gl"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_sky_simple"].libs = ["osgdb_osgearth_sky_simple" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_sky_simple"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_sky_simple"].requires = ["osgEarth", "opengl::opengl"]

        self.cpp_info.components["osgdb_template"].libs = ["osgdb_template" + libsuffix]
        self.cpp_info.components["osgdb_template"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_template"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_terrainshader"].libs = ["osgdb_osgearth_terrainshader" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_terrainshader"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_terrainshader"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_vdatum_egm2008"].libs = ["osgdb_osgearth_vdatum_egm2008" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_vdatum_egm2008"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_vdatum_egm2008"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_vdatum_egm84"].libs = ["osgdb_osgearth_vdatum_egm84" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_vdatum_egm84"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_vdatum_egm84"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_vdatum_egm96"].libs = ["osgdb_osgearth_vdatum_egm96" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_vdatum_egm96"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_vdatum_egm96"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_viewpoints"].libs = ["osgdb_osgearth_viewpoints" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_viewpoints"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_viewpoints"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_webp"].libs = ["osgdb_webp" + libsuffix]
        self.cpp_info.components["osgdb_webp"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_webp"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_scriptengine_javascript_qjs"].libs = ["osgdb_osgearth_scriptengine_javascript_qjs" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_scriptengine_javascript_qjs"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_scriptengine_javascript_qjs"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_osgearth_scriptengine_javascript_duktape"].libs = ["osgdb_osgearth_scriptengine_javascript_duktape" + libsuffix]
        self.cpp_info.components["osgdb_osgearth_scriptengine_javascript_duktape"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_osgearth_scriptengine_javascript_duktape"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_gltf"].libs = ["osgdb_gltf" + libsuffix]
        self.cpp_info.components["osgdb_gltf"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_gltf"].requires = ["osgEarth", "draco::draco"]

        self.cpp_info.components["osgdb_fastdxt"].libs = ["osgdb_fastdxt" + libsuffix]
        self.cpp_info.components["osgdb_fastdxt"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_fastdxt"].requires = ["osgEarth"]

        self.cpp_info.components["osgdb_lerc"].libs = ["osgdb_lerc" + libsuffix]
        self.cpp_info.components["osgdb_lerc"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["osgdb_lerc"].requires = ["osgEarth", "lerc::lerc"]


        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_osgearth_vdatum_egm2008.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_osgearth_vdatum_egm84.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_osgearth_vdatum_egm96.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_osgearth_viewpoints.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_webp.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_osgearth_scriptengine_javascript_qjs.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_osgearth_scriptengine_javascript_duktape.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_gltf.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_fastdxt.so" to ""
        # -- Set non-toolchain portion of runtime path of "/home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/osgPlugins-3.6.5/osgdb_lerc.so" to ""
        # -- Installing: /home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/libosgEarth.so.3.8.0
        #-- Installing: /home/conan/.conan2/p/b/osgeae1dc417d448ff/p/lib/libosgEarth.so.185
