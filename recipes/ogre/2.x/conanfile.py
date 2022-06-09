import glob, os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import textwrap

class OgreCmakeConan(ConanFile):
    name = "OGRE"
    license = "MIT"
    homepage = "https://www.ogre3d.org/tag/v2-1"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A scene-oriented, flexible 3D engine written in C++ "
    topics = ("Graphics", "Rendering", "Engine", "C++")

    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

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
        "OGRE_STATIC": [True, False],
        "OPENEXR_Half_LIBRARY": "ANY",
        "OPENEXR_Half_LIBRARY_DEBUG": "ANY",
        "OPENEXR_INCLUDE_DIR": "ANY",
        "OPENEXR_Iex_LIBRARY": "ANY",
        "OPENEXR_Iex_LIBRARY_DEBUG": "ANY",
        "OPENEXR_IlmImf_LIBRARY": "ANY",
        "OPENEXR_IlmImf_LIBRARY_DEBUG": "ANY",
        "OPENEXR_IlmThread_LIBRARY": "ANY",
        "OPENEXR_IlmThread_LIBRARY_DEBUG": "ANY",
        "Qt5_DIR": "ANY",
        "SDL2_DIR": "ANY",
        "pugixml_DIR": "ANY"
    }

    # default options copied from https://github.com/StatelessStudio/ogre-conan/blob/master/conanfile.py
    default_options = {
        "shared": True,
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
        "OGRE_BUILD_DEPENDENCIES": True,
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
        "OGRE_INSTALL_PDB": True,
        "OGRE_INSTALL_SAMPLES": True,
        "OGRE_INSTALL_TOOLS": True,
        "OGRE_INSTALL_VSPROPS": False,
        "OGRE_NODELESS_POSITIONING": True,
        "OGRE_PROFILING_REMOTERY_PATH": "",
        "OGRE_RESOURCEMANAGER_STRICT": 2,
        "OGRE_STATIC": False,
        "OPENEXR_Half_LIBRARY": "OPENEXR_Half_LIBRARY-NOTFOUND",
        "OPENEXR_Half_LIBRARY_DEBUG": "OPENEXR_Half_LIBRARY_DEBUG-NOTFOUND",
        "OPENEXR_INCLUDE_DIR": "OPENEXR_INCLUDE_DIR-NOTFOUND",
        "OPENEXR_Iex_LIBRARY": "OPENEXR_Iex_LIBRARY-NOTFOUND",
        "OPENEXR_Iex_LIBRARY_DEBUG": "OPENEXR_Iex_LIBRARY_DEBUG-NOTFOUND",
        "OPENEXR_IlmImf_LIBRARY": "OPENEXR_IlmImf_LIBRARY-NOTFOUND",
        "OPENEXR_IlmImf_LIBRARY_DEBUG": "OPENEXR_IlmImf_LIBRARY_DEBUG-NOTFOUND",
        "OPENEXR_IlmThread_LIBRARY": "OPENEXR_IlmThread_LIBRARY-NOTFOUND",
        "OPENEXR_IlmThread_LIBRARY_DEBUG": "OPENEXR_IlmThread_LIBRARY_DEBUG-NOTFOUND",
        "Qt5_DIR": "Qt5_DIR-NOTFOUND",
        "SDL2_DIR": "${ogre-build-dir}/Dependencies/cmake",
        "pugixml_DIR": "${ogre-build-dir}/Dependencies/lib/cmake/pugixml"
    }

    exports_sources = "CMakeLists.txt", "patches/**"
    _cmake = None

    def requirements(self):
        self.requires("freetype/2.11.1")
        #self.requires("freeimage/3.18.0")

    def validate(self):
        """
         OGRE 1.x is very old and will not work with latest gcc, clang and msvc compielrs
         TODO: determine incompatible msvc compilers
        """
        if self.settings.compiler == "gcc" and self.settings.compiler.version == 11:
            raise ConanInvalidConfiguration("OGRE 1.x not supported with gcc 11")
        if self.settings.compiler == "clang" and self.settings.compiler.version == 13:
            raise ConanInvalidConfiguration("OGRE 1.x not supported with clang 13")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("ogre*")[0], self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        #tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        #tools.rmdir(os.path.join(self.package_folder, "lib", "share"))
        #tools.rmdir(os.path.join(self.package_folder, "lib", "OGRE", "cmake"))
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
        include_prefix = f"{self.package_folder}/OGRE"
        components = {
            "OgreMain":  {"requires" : ["freetype::freetype"], "libs": ["OgreMain"], "include": [include_prefix]},
            "Bites":  {"requires" : [], "libs": ["OgreBites"], "include": [include_prefix, f"{include_prefix}/Bites"]},
            "HLMS" :  {"requires" : [], "libs": ["OgreHLMS"], "include": [include_prefix, f"{include_prefix}/HLMS"]},
            "MeshLodGenerator" :  {"requires" : [], "libs": ["OgreMeshLoadGenerator"], "include": [include_prefix, f"{include_prefix}/MeshLoadGenerator"]},
            "Overlay" :  {"requires" : [], "libs": ["OgreOverlay"], "include": [include_prefix, f"{include_prefix}/Overlay"]},
            "Paging" :  {"requires" : [], "libs": ["OgrePaging"], "include": [include_prefix, f"{include_prefix}/Paging"]},
            "Property" :  {"requires" : [], "libs": ["OgreProperty"], "include": [include_prefix, f"{include_prefix}/Property"]},
            "Python" :  {"requires" : [], "libs": ["OgrePython"], "include": [include_prefix, f"{include_prefix}/Python"]},
            "RTShaderSystem" :  {"requires" : [], "libs": ["OgreRTShaderSystem"], "include": [include_prefix, f"{include_prefix}/RTShaderSystem"]},
            "Terrain" :  {"requires" : [], "libs": ["OgreTerrain"], "include": [include_prefix, f"{include_prefix}/Terrain"]},
            "Volume" :  {"requires" : [], "libs": ["OgreVolume"], "include": [include_prefix, f"{include_prefix}/Volume"]}
        }

        return components

    def package_info(self):
        version_major = tools.Version(self.version).major
        self.cpp_info.names["cmake_find_package"] = "OGRE"
        self.cpp_info.names["cmake_find_package_multi"] = "OGRE"
        self.cpp_info.names["cmake_paths"] = "OGRE"

        for comp, values in self._components.items():
            self.cpp_info.components[comp].names["cmake_find_package"] = comp
            self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
            self.cpp_info.components[comp].names["cmake_paths"] = comp
            self.cpp_info.components[comp].libs = values.get("libs")
            self.cpp_info.components[comp].requires = values.get("requires")
            self.cpp_info.components[comp].includedirs = values.get("include")
            self.cpp_info.components[comp].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_paths"] = [self._module_file_rel_path]

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")
