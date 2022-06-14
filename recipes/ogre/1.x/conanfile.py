import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import conan.tools.files
import textwrap, shutil
import functools

class ogrecmakeconan(ConanFile):
    name = "ogre"
    license = "MIT"
    homepage = "https://github.com/OGRECave/ogre"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A scene-oriented, flexible 3D engine written in C++ "
    topics = ("graphics", "rendering", "engine", "c++")

    settings = "os", "compiler", "build_type", "arch"

    generators = "cmake", "cmake_find_package"
    exports_sources = "CMakeLists.txt", "patches/**"
    #options copied from https://github.com/StatelessStudio/ogre-conan/blob/master/conanfile.py
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cp_bin_dir": "ANY",
        "cp_media_dir": "ANY",
        "disable_plugins": [True, False],
        "OGRE_ASSERT_MODE": "ANY",
        "OGRE_BUILD_COMPONENT_BITES": [True, False],
        "OGRE_BUILD_COMPONENT_CSHARP": [True, False],
        "OGRE_BUILD_COMPONENT_HLMS": [True, False],
        "OGRE_BUILD_COMPONENT_JAVA": [True, False],
        "OGRE_BUILD_COMPONENT_MESHLODGENERATOR": [True, False],
        "OGRE_BUILD_COMPONENT_OVERLAY": [True, False],
        "OGRE_BUILD_COMPONENT_OVERLAY_IMGUI": [True, False],
        "OGRE_BUILD_COMPONENT_PAGING": [True, False],
        "OGRE_BUILD_COMPONENT_PROPERTY": [True, False],
        "OGRE_BUILD_COMPONENT_PYTHON": [True, False],
        "OGRE_BUILD_COMPONENT_RTSHADERSYSTEM": [True, False],
        "OGRE_BUILD_COMPONENT_TERRAIN": [True, False],
        "OGRE_BUILD_COMPONENT_VOLUME": [True, False],
        "OGRE_BUILD_DEPENDENCIES": [True, False],
        "OGRE_BUILD_PLUGIN_BSP": [True, False],
        "OGRE_BUILD_PLUGIN_DOT_SCENE": [True, False],
        "OGRE_BUILD_PLUGIN_OCTREE": [True, False],
        "OGRE_BUILD_PLUGIN_PCZ": [True, False],
        "OGRE_BUILD_PLUGIN_PFX": [True, False],
        "OGRE_BUILD_PLUGIN_STBI": [True, False],
        "OGRE_BUILD_RENDERSYSTEM_D3D11": [True, False],
        "OGRE_BUILD_RENDERSYSTEM_GL": [True, False],
        "OGRE_BUILD_RENDERSYSTEM_GL3PLUS": [True, False],
        "OGRE_BUILD_RTSHADERSYSTEM_SHADERS": [True, False],
        "OGRE_BUILD_SAMPLES": [True, False],
        "OGRE_BUILD_TESTS": [True, False],
        "OGRE_BUILD_TOOLS": [True, False],
        "OGRE_CONFIG_ENABLE_QUAD_BUFFER_STEREO": [True, False],
        "OGRE_CONFIG_FILESYSTEM_UNICODE": [True, False],
        "OGRE_CONFIG_THREADS": "ANY",
        "OGRE_CONFIG_THREAD_PROVIDER": "ANY",
        "OGRE_ENABLE_PRECOMPILED_HEADERS": [True, False],
        "OGRE_INSTALL_PDB": [True, False],
        "OGRE_INSTALL_SAMPLES": [True, False],
        "OGRE_INSTALL_TOOLS": [True, False],
        "OGRE_INSTALL_VSPROPS": [True, False],
        "OGRE_NODELESS_POSITIONING": [True, False],
        "OGRE_PROFILING_REMOTERY_PATH": "ANY",
        "OGRE_RESOURCEMANAGER_STRICT": "ANY",
        "ogre_static": [True, False],
        "ogre_set_double": [True, False],
        "ogre_glsupport_use_egl": [True, False],
        "OpenEXR_Half_LIBRARY": "ANY",
        "OpenEXR_Half_LIBRARY_DEBUG": "ANY",
        "OpenEXR_INCLUDE_DIR": "ANY",
        "OpenEXR_Iex_LIBRARY": "ANY",
        "OpenEXR_Iex_LIBRARY_DEBUG": "ANY",
        "OpenEXR_IlmImf_LIBRARY": "ANY",
        "OpenEXR_IlmImf_LIBRARY_DEBUG": "ANY",
        "OpenEXR_IlmThread_LIBRARY": "ANY",
        "OpenEXR_IlmThread_LIBRARY_DEBUG": "ANY",
        "Qt5_DIR": "ANY",
        "SDL2_DIR": "ANY",
        "pugixml_DIR": "ANY"
    }

    # default options copied from https://github.com/StatelessStudio/ogre-conan/blob/master/conanfile.py
    default_options = {
        "shared": False,
        "fPIC": True,
        "cp_bin_dir": "bin",
        "cp_media_dir": "Media",
        "disable_plugins": False,
        "OGRE_ASSERT_MODE": 1,
        "OGRE_BUILD_COMPONENT_BITES": True,
        "OGRE_BUILD_COMPONENT_CSHARP": False,
        "OGRE_BUILD_COMPONENT_HLMS": True,
        "OGRE_BUILD_COMPONENT_JAVA": False,
        "OGRE_BUILD_COMPONENT_MESHLODGENERATOR": True,
        "OGRE_BUILD_COMPONENT_OVERLAY": True,
        "OGRE_BUILD_COMPONENT_OVERLAY_IMGUI": True,
        "OGRE_BUILD_COMPONENT_PAGING": True,
        "OGRE_BUILD_COMPONENT_PROPERTY": True,
        "OGRE_BUILD_COMPONENT_PYTHON": True,
        "OGRE_BUILD_COMPONENT_RTSHADERSYSTEM": True,
        "OGRE_BUILD_COMPONENT_TERRAIN": True,
        "OGRE_BUILD_COMPONENT_VOLUME": True,
        "OGRE_BUILD_DEPENDENCIES": False,
        "OGRE_BUILD_PLUGIN_BSP": True,
        "OGRE_BUILD_PLUGIN_DOT_SCENE": True,
        "OGRE_BUILD_PLUGIN_OCTREE": True,
        "OGRE_BUILD_PLUGIN_PCZ": True,
        "OGRE_BUILD_PLUGIN_PFX": True,
        "OGRE_BUILD_PLUGIN_STBI": True,
        "OGRE_BUILD_RENDERSYSTEM_D3D11": True,
        "OGRE_BUILD_RENDERSYSTEM_GL": True,
        "OGRE_BUILD_RENDERSYSTEM_GL3PLUS": True,
        "OGRE_BUILD_RTSHADERSYSTEM_SHADERS": True,
        "OGRE_BUILD_SAMPLES": True,
        "OGRE_BUILD_TESTS": False,
        "OGRE_BUILD_TOOLS": True,
        "OGRE_CONFIG_ENABLE_QUAD_BUFFER_STEREO": False,
        "OGRE_CONFIG_FILESYSTEM_UNICODE": True,
        "OGRE_CONFIG_THREADS": 3,
        "OGRE_CONFIG_THREAD_PROVIDER": "std",
        "OGRE_ENABLE_PRECOMPILED_HEADERS": True,
        "OGRE_INSTALL_PDB": False,
        "OGRE_INSTALL_SAMPLES": True,
        "OGRE_INSTALL_TOOLS": True,
        "OGRE_INSTALL_VSPROPS": False,
        "OGRE_NODELESS_POSITIONING": True,
        "OGRE_PROFILING_REMOTERY_PATH": "",
        "OGRE_RESOURCEMANAGER_STRICT": 2,
        "ogre_static": True,
        "ogre_set_double": False,
        "ogre_glsupport_use_egl": True,
        "OpenEXR_Half_LIBRARY": "OpenEXR_Half_LIBRARY-NOTFOUND",
        "OpenEXR_Half_LIBRARY_DEBUG": "OpenEXR_Half_LIBRARY_DEBUG-NOTFOUND",
        "OpenEXR_INCLUDE_DIR": "OpenEXR_INCLUDE_DIR-NOTFOUND",
        "OpenEXR_Iex_LIBRARY": "OpenEXR_Iex_LIBRARY-NOTFOUND",
        "OpenEXR_Iex_LIBRARY_DEBUG": "OpenEXR_Iex_LIBRARY_DEBUG-NOTFOUND",
        "OpenEXR_IlmImf_LIBRARY": "OpenEXR_IlmImf_LIBRARY-NOTFOUND",
        "OpenEXR_IlmImf_LIBRARY_DEBUG": "OpenEXR_IlmImf_LIBRARY_DEBUG-NOTFOUND",
        "OpenEXR_IlmThread_LIBRARY": "OpenEXR_IlmThread_LIBRARY-NOTFOUND",
        "OpenEXR_IlmThread_LIBRARY_DEBUG": "OpenEXR_IlmThread_LIBRARY_DEBUG-NOTFOUND",
        "Qt5_DIR": "Qt5_DIR-NOTFOUND",
        "SDL2_DIR": "${ogre-build-dir}/Dependencies/cmake",
        "pugixml_DIR": "${ogre-build-dir}/Dependencies/lib/cmake/pugixml"
    }
    exports_sources = "CMakeLists.txt", "patches/**"
    short_paths = True

    def requirements(self):
        self.requires("cppunit/1.15.1")
        self.requires("freeimage/3.18.0")
        self.requires("boost/1.75.0")
        self.requires("freetype/2.11.1")
        self.requires("openexr/2.5.7")
        self.requires("poco/1.11.2")
        self.requires("tbb/2020.3")
        self.requires("zlib/1.2.12")
        self.requires("zziplib/0.13.71")
        self.requires("openssl/1.1.1o", override=True)
        self.requires("xorg/system")
        self.requires("glu/system")
        if self.options.ogre_glsupport_use_egl and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("egl/system")
        else:
            self.requires("libglvnd/1.4.0")
        

    def validate(self):
        """
         OGRE 1.x is very old and will not work with latest gcc, clang and msvc compielrs
         TODO: determine incompatible msvc compilers
        """
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) >= 9:
            raise ConanInvalidConfiguration("OGRE 1.x not supported with gcc 11")
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) >= 9:
            raise ConanInvalidConfiguration("OGRE 1.x not supported with clang 13")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OGRE_STATIC"] = not self.options.shared
        cmake.definitions["OGRE_CONFIG_DOUBLE"] = self.options.ogre_set_double
        cmake.definitions["OGRE_CONFIG_NODE_INHERIT_TRANSFORM"] = False
        cmake.definitions["OGRE_GLSUPPORT_USE_EGL"] = self.options.ogre_glsupport_use_egl
        if not tools.valid_min_cppstd(self, 11):
            cmake.definitions["CMAKE_CXX_STANDARD"] = 11 # for OpenEXR
        cmake.definitions["OGRE_BUILD_TESTS"] = self.options.OGRE_BUILD_TESTS
        cmake.definitions["OGRE_BUILD_SAMPLES"] = self.options.OGRE_BUILD_SAMPLES
        cmake.definitions["OGRE_INSTALL_SAMPLES"] = self.options.OGRE_INSTALL_SAMPLES
        cmake.definitions["OGRE_INSTALL_PDB"] = self.options.OGRE_INSTALL_PDB
        cmake.configure()
        return cmake


    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        # the pkgs below are not available as conan recipes yet
        # TODO: delte line 200-208 once the conan recipes are available
        ogre_pkg_modules = ["AMDQBS", "Cg", "HLSL2GLSL", "GLSLOptimizer", "OpenGLES", "OpenGLES2", "OpenGLES3", "SDL2", "Softimage", "Wix"]
        ogre_pkg_module_path = os.path.join(self.build_folder, self._source_subfolder, "CMake", "Packages")
        for pkg_module in ogre_pkg_modules:
            pkg_path = os.path.join(ogre_pkg_module_path, f"Find{pkg_module}.cmake")
            if os.path.isfile(pkg_path):
                shutil.copy(pkg_path, self.build_folder)
            else:
                raise RuntimeError(f"The file Find{pkg_module}.cmake is not present in f{ogre_pkg_module_path}!")


        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "OGRE", "cmake"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
            tools.Version(self.version)
        )
        
        
    @staticmethod
    def _create_cmake_module_variables(module_file, version):
        content = textwrap.dedent("""\
            set(OGRE_PREFIX_DIR ${{CMAKE_CURRENT_LIST_DIR}}/../..)
            set(OGRE{major}_VERSION_MAJOR {major})
            set(OGRE{major}_VERSION_MINOR {minor})
            set(OGRE{major}_VERSION_PATCH {patch})
            set(OGRE{major}_VERSION_STRING "{major}.{minor}.{patch}")

            set(OGRE_MEDIA_DIR "${{OGRE_PREFIX_DIR}}/share/OGRE/Media")
            set(OGRE_PLUGIN_DIR "${{OGRE_PREFIX_DIR}}/lib/OGRE")
            set(OGRE_CONFIG_DIR "${{OGRE_PREFIX_DIR}}/share/OGRE") 
        """.format(major=version.major, minor=version.minor, patch=version.patch))
        tools.save(module_file, content)


    @property
    def _components(self):
        pkg_name = "OGRE"
        include_prefix = os.path.join("include", "OGRE")
        components = {
            "OgreMain":  {"requires" : ["boost::boost", "cppunit::cppunit", "freeimage::freeimage", "openexr::openexr","freetype::freetype", "tbb::tbb", "xorg::xorg", "zlib::zlib", "zziplib::zziplib", "poco::poco","glu::glu"], 
                            "libs": ["OgreMain"], "include": [include_prefix]},
            "Bites":  {"requires" : ["OgreMain", "Overlay"], "libs": ["OgreBites"], "include": [include_prefix, f"{include_prefix}/Bites"]},
            "HLMS" :  {"requires" : ["OgreMain"], "libs": ["OgreHLMS"], "include": [include_prefix, f"{include_prefix}/HLMS"]},
            "MeshLodGenerator" :  {"requires" : ["OgreMain"], "libs": ["OgreMeshLoadGenerator"], "include": [include_prefix, f"{include_prefix}/MeshLoadGenerator"]},
            "Overlay" :  {"requires" : ["OgreMain"], "libs": ["OgreOverlay"], "include": [include_prefix, f"{include_prefix}/Overlay"]},
            "Paging" :  {"requires" : ["OgreMain"], "libs": ["OgrePaging"], "include": [include_prefix, f"{include_prefix}/Paging"]},
            "Property" :  {"requires" : ["OgreMain"], "libs": ["OgreProperty"], "include": [include_prefix, f"{include_prefix}/Property"]},
            "Python" :  {"requires" : ["OgreMain"], "libs": ["OgrePython"], "include": [include_prefix, f"{include_prefix}/Python"]},
            "RTShaderSystem" :  {"requires" : ["OgreMain"], "libs": ["OgreRTShaderSystem"], "include": [include_prefix, f"{include_prefix}/RTShaderSystem"]},
            "Terrain" :  {"requires" : ["OgreMain"], "libs": ["OgreTerrain"], "include": [include_prefix, f"{include_prefix}/Terrain"]},
            "Volume" :  {"requires" : ["OgreMain"], "libs": ["OgreVolume"], "include": [include_prefix, f"{include_prefix}/Volume"]}
        }

        return components

    def package_info(self):
        version_major = tools.Version(self.version).major
        self.cpp_info.set_property("cmake_file_name", "OGRE")
        self.cpp_info.names["cmake_find_package"] = "OGRE"
        self.cpp_info.names["cmake_find_package_multi"] = "OGRE"
        self.cpp_info.names["cmake_paths"] = "OGRE"

        for comp, values in self._components.items():
            self.cpp_info.components[comp].names["cmake_find_package"] = comp
            self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
            self.cpp_info.components[comp].names["cmake_paths"] = comp
            self.cpp_info.components[comp].libs = values.get("libs")
            self.cpp_info.components[comp].requires = values.get("requires")
            self.cpp_info.components[comp].set_property("cmake_target_name", f"OGRE::{comp}")
            self.cpp_info.components[comp].includedirs = values.get("include")
            self.cpp_info.components[comp].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_paths"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].builddirs.append(self._module_file_rel_path)
            if self.settings.os == "Linux":
                self.cpp_info.components[comp].system_libs.append("pthread")

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")
