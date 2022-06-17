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

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cp_bin_dir": "ANY",
        "cp_media_dir": "ANY",
        "disable_plugins": [True, False],
        "ogre_assert_mode": "ANY",
        "ogre_build_component_bites": [True, False],
        "ogre_build_component_hlms": [True, False],
        "ogre_build_component_meshlodgenerator": [True, False],
        "ogre_build_component_overlay": [True, False],
        "ogre_build_component_paging": [True, False],
        "ogre_build_component_property": [True, False],
        "ogre_build_component_python": [True, False],
        "ogre_build_component_rtshadersystem": [True, False],
        "ogre_build_component_terrain": [True, False],
        "ogre_build_component_volume": [True, False],
        "ogre_build_dependencies": [True, False],
        "ogre_build_plugin_bsp": [True, False],
        "ogre_build_plugin_octree": [True, False],
        "ogre_build_plugin_pcz": [True, False],
        "ogre_build_plugin_pfx": [True, False],
        "ogre_build_rendersystem_d3d11": [True, False],
        "ogre_build_rendersystem_gl": [True, False],
        "ogre_build_rendersystem_gl3plus": [True, False],
        "ogre_build_samples": [True, False],
        "ogre_build_tests": [True, False],
        "ogre_build_tools": [True, False],
        "ogre_config_enable_quad_buffer_stereo": [True, False],
        "ogre_config_filesystem_unicode": [True, False],
        "ogre_config_threads": "ANY",
        "ogre_config_thread_provider": "ANY",
        "ogre_config_enable_freeimage": [True, False],
        "ogre_install_pdb": [True, False],
        "ogre_install_samples": [True, False],
        "ogre_install_tools": [True, False],
        "ogre_install_vsprops": [True, False],
        "ogre_resourcemanager_strict": "ANY",
        "ogre_static": [True, False],
        "ogre_set_double": [True, False],
        "ogre_glsupport_use_egl": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "cp_bin_dir": "bin",
        "cp_media_dir": "Media",
        "disable_plugins": False,
        "ogre_assert_mode": 1,
        "ogre_build_component_bites": True,
        "ogre_build_component_hlms": True,
        "ogre_build_component_meshlodgenerator": True,
        "ogre_build_component_overlay": True,
        "ogre_build_component_paging": True,
        "ogre_build_component_property": True,
        "ogre_build_component_python": False,
        "ogre_build_component_rtshadersystem": True,
        "ogre_build_component_terrain": True,
        "ogre_build_component_volume": True,
        "ogre_build_dependencies": False,
        "ogre_build_plugin_bsp": True,
        "ogre_build_plugin_octree": True,
        "ogre_build_plugin_pcz": True,
        "ogre_build_plugin_pfx": True,
        "ogre_build_rendersystem_d3d11": True,
        "ogre_build_rendersystem_gl": True,
        "ogre_build_rendersystem_gl3plus": True,
        "ogre_build_samples": False,
        "ogre_build_tests": False,
        "ogre_build_tools": True,
        "ogre_config_enable_quad_buffer_stereo": False,
        "ogre_config_filesystem_unicode": True,
        "ogre_config_threads": 3,
        "ogre_config_thread_provider": "std",
        "ogre_config_enable_freeimage": True,
        "ogre_install_pdb": False,
        "ogre_install_samples": False,
        "ogre_install_tools": True,
        "ogre_install_vsprops": False,
        "ogre_resourcemanager_strict": 2,
        "ogre_static": True,
        "ogre_set_double": False,
        "ogre_glsupport_use_egl": True
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
        self.requires("sdl/2.0.20")
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
            raise ConanInvalidConfiguration("OGRE 1.x not supported with gcc version greater than 9")
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) >= 9:
            raise ConanInvalidConfiguration("OGRE 1.x not supported with clang version greater than 9")

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
        cmake.definitions["OGRE_BUILD_TESTS"] = self.options.ogre_build_tests
        cmake.definitions["OGRE_ASSERT_MODE"] = self.options.ogre_assert_mode
        cmake.definitions["OGRE_BUILD_COMPONENT_BITES"]  = self.options.ogre_build_component_bites
        cmake.definitions["OGRE_BUILD_COMPONENT_HLMS"] = self.options.ogre_build_component_hlms
        cmake.definitions["OGRE_BUILD_COMPONENT_MESHLODGENERATOR"] = self.options.ogre_build_component_meshlodgenerator
        cmake.definitions["OGRE_BUILD_COMPONENT_OVERLAY"] = self.options.ogre_build_component_overlay
        cmake.definitions["OGRE_BUILD_COMPONENT_PAGING"] = self.options.ogre_build_component_paging
        cmake.definitions["OGRE_BUILD_COMPONENT_PROPERTY"] = self.options.ogre_build_component_property
        cmake.definitions["OGRE_BUILD_COMPONENT_PYTHON"] = self.options.ogre_build_component_python
        cmake.definitions["OGRE_BUILD_COMPONENT_RTSHADERSYSTEM"] = self.options.ogre_build_component_rtshadersystem
        cmake.definitions["OGRE_BUILD_COMPONENT_TERRAIN"] = self.options.ogre_build_component_terrain
        cmake.definitions["OGRE_BUILD_COMPONENT_VOLUME"] = self.options.ogre_build_component_volume
        cmake.definitions["OGRE_BUILD_DEPENDENCIES"] = self.options.ogre_build_dependencies
        cmake.definitions["OGRE_BUILD_PLUGIN_BSP"] = self.options.ogre_build_plugin_bsp
        cmake.definitions["OGRE_BUILD_PLUGIN_OCTREE"] = self.options.ogre_build_plugin_octree
        cmake.definitions["OGRE_BUILD_PLUGIN_PCZ"] = self.options.ogre_build_plugin_pcz
        cmake.definitions["OGRE_BUILD_PLUGIN_PFX"] = self.options.ogre_build_plugin_pfx
        cmake.definitions["OGRE_BUILD_RENDERSYSTEM_D3D11"] = self.options.ogre_build_rendersystem_d3d11
        cmake.definitions["OGRE_BUILD_RENDERSYSTEM_GL"] = self.options.ogre_build_rendersystem_gl
        cmake.definitions["OGRE_BUILD_RENDERSYSTEM_GL3PLUS"] = self.options.ogre_build_rendersystem_gl3plus
        cmake.definitions["OGRE_BUILD_SAMPLES"] = self.options.ogre_build_samples
        cmake.definitions["OGRE_BUILD_TOOLS"] = self.options.ogre_build_tools
        cmake.definitions["OGRE_CONFIG_ENABLE_QUAD_BUFFER_STEREO"] = self.options.ogre_config_enable_quad_buffer_stereo
        cmake.definitions["OGRE_CONFIG_FILESYSTEM_UNICODE"] = self.options.ogre_config_filesystem_unicode
        cmake.definitions["OGRE_CONFIG_THREADS"] = self.options.ogre_config_threads
        cmake.definitions["OGRE_CONFIG_THREAD_PROVIDER"] = self.options.ogre_config_thread_provider
        cmake.definitions["OGRE_CONFIG_ENABLE_FREEIMAGE"] = self.options.ogre_config_enable_freeimage
        cmake.definitions["OGRE_INSTALL_PDB"] = self.options.ogre_install_pdb
        cmake.definitions["OGRE_INSTALL_SAMPLES"] = self.options.ogre_install_samples
        cmake.definitions["OGRE_INSTALL_TOOLS"] = self.options.ogre_install_tools
        cmake.definitions["OGRE_RESOURCEMANAGER_STRICT"] = self.options.ogre_resourcemanager_strict
        if self.settings.os == "Windows":
            cmake.definitions["OGRE_INSTALL_VSPROPS"] = self.options.ogre_install_vsprops
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
        self.copy(pattern="License.md", dst="licenses", src=os.path.join(self._source_subfolder, "Docs"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "OGRE", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
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
            "OgreMain":  {"requires" : ["boost::boost", "cppunit::cppunit", "freeimage::freeimage", "openexr::openexr","freetype::freetype", 
                                        "sdl::sdl", "tbb::tbb", "xorg::xorg", "zlib::zlib", "zziplib::zziplib", "poco::poco","glu::glu", "egl::egl"], 
                            "libs": ["OgreMain"], "include": [include_prefix]},
            "Bites":  {"requires" : ["OgreMain", "Overlay"], "libs": ["OgreBites"], "include": ["include", include_prefix, f"{include_prefix}/Bites"]},
            "HLMS" :  {"requires" : ["OgreMain"], "libs": ["OgreHLMS"], "include": ["include", include_prefix, f"{include_prefix}/HLMS"]},
            "MeshLodGenerator" :  {"requires" : ["OgreMain"], "libs": ["OgreMeshLodGenerator"], "include": ["include", include_prefix, f"{include_prefix}/MeshLodGenerator"]},
            "Overlay" :  {"requires" : ["OgreMain"], "libs": ["OgreOverlay"], "include": ["include", include_prefix, f"{include_prefix}/Overlay"]},
            "Paging" :  {"requires" : ["OgreMain"], "libs": ["OgrePaging"], "include": ["include", include_prefix, f"{include_prefix}/Paging"]},
            "Property" :  {"requires" : ["OgreMain"], "libs": ["OgreProperty"], "include": ["include", include_prefix, f"{include_prefix}/Property"]},
            "RTShaderSystem" :  {"requires" : ["OgreMain"], "libs": ["OgreRTShaderSystem"], "include": ["include", include_prefix, f"{include_prefix}/RTShaderSystem"]},
            "Terrain" :  {"requires" : ["OgreMain"], "libs": ["OgreTerrain"], "include": ["include", include_prefix, f"{include_prefix}/Terrain"]},
            "Volume" :  {"requires" : ["OgreMain"], "libs": ["OgreVolume"], "include": ["include", include_prefix, f"{include_prefix}/Volume"]}
            
        }

        if self.options.ogre_static:
            for _, values in components.items():
                libs = [lib + "Static" for lib in values.get("libs")]
                values["libs"] = libs

        if self.options.ogre_build_tests:
            components["OgreMain"]["requires"].append("cppunit::cppunit")

        if self.options.ogre_build_component_python:
            components["Python"] = {"requires" : ["OgreMain"], "libs": ["OgrePython"], "include": ["include", include_prefix, f"{include_prefix}/Python"]}

        if self.settings.build_type == "Debug":
            for _, values in components.items():
                libs = [lib + "_d" for lib in values.get("libs")]
                values["libs"] = libs


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
            
            self.cpp_info.components[comp].builddirs.append(self._module_file_rel_dir)
            self.cpp_info.components[comp].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_paths"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].builddirs.append(self._module_file_rel_path)
            if self.settings.os == "Linux":
                self.cpp_info.components[comp].system_libs.append("pthread")
            
            # TODO: bindir, plugindir, plugin_include_dirs plugin_lib_dirs
            

    @property
    def _module_file_rel_dir(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_file_rel_dir, f"conan-official-{self.name}-variables.cmake")
