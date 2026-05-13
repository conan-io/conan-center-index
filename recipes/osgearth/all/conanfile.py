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
        # INFO: Transitive headers osgEarth/Notify:8 #include <osg/Notify>
        self.requires("openscenegraph/3.6.5", transitive_headers=True)
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("lerc/[>=4.0.1 <5]")
        self.requires("protobuf/[>=5.27.0 <7]")
        self.requires("geos/[>=3.12.0 <4]")
        self.requires("sqlite3/[>=3.42 <4]")
        self.requires("spdlog/[>=1.11 <2]")
        
    def validate(self):
        check_min_cppstd(self, 17)
        
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        libsuffix = {"Debug": "d", "MinSizeRel": "s"}.get(str(self.settings.build_type), "") if self.settings.os == "Windows" else ""
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
        self.cpp_info.components["osgEarthImGui"].libs = ["osgEarthImGui" + libsuffix]
        self.cpp_info.components["osgEarthImGui"].set_property("cmake_target_name", "osgEarth::osgEarthImGui")
        self.cpp_info.components["osgEarthImGui"].requires = ["osgEarth", "opengl::opengl"]

        self.cpp_info.components["plugins"].libdirs = [os.path.join("lib", f"osgPlugins-{openscenegraph_version}")]
        self.cpp_info.components["plugins"].set_property("cmake_target_name", "osgEarth::plugins")
        self.cpp_info.components["plugins"].requires = ["osgEarth", "opengl::opengl", "lerc::lerc"]
