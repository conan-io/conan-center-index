import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, save, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class OgreConanFile(ConanFile):
    name = "ogre"
    description = "A scene-oriented, flexible 3D engine written in C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OGRECave/ogre"
    topics = ("graphics", "rendering", "engine", "c++")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "resourcemanager_strict":  ["PEDANTIC", "STRICT"],
        "build_rendersystem_d3d9": [True, False],
        "build_rendersystem_d3d11": [True, False],
        "build_rendersystem_gl3plus": [True, False],
        "build_rendersystem_gl": [True, False],
        "build_rendersystem_gles2": [True, False],
        "build_rendersystem_metal": [True, False],
        "build_rendersystem_tiny": [True, False],
        "build_component_paging": [True, False],
        "build_component_meshlodgenerator": [True, False],
        "build_component_terrain": [True, False],
        "build_component_volume": [True, False],
        "build_component_property": [True, False],
        "build_component_overlay": [True, False],
        "build_component_overlay_imgui": [True, False],
        "build_component_bites": [True, False],
        "build_component_bullet": [True, False],
        "bites_static_plugins": [True, False],
        "build_component_rtshadersystem": [True, False],
        "build_rtshadersystem_shaders": [True, False],
        "build_tools": [True, False],
        "build_xsiexporter": [True, False],
        # "build_libs_as_frameworks": [True, False],
        "build_plugin_assimp": [True, False],
        "build_plugin_bsp": [True, False],
        "build_plugin_dot_scene": [True, False],
        "build_plugin_exrcodec": [True, False],
        "build_plugin_freeimage": [True, False],
        "build_plugin_octree": [True, False],
        "build_plugin_pcz": [True, False],
        "build_plugin_pfx": [True, False],
        "build_plugin_stbi": [True, False],
        "config_enable_meshlod": [True, False],
        "config_double": [True, False],
        "config_node_inherit_transform": [True, False],
        "config_threads": [True, False],
        "config_enable_dds": [True, False],
        "config_enable_pvrtc": [True, False],
        "config_enable_etc": [True, False],
        "config_enable_astc": [True, False],
        "config_enable_quad_buffer_stereo": [True, False],
        "config_enable_viewport_orientationmode": [True, False],
        "config_enable_gles2_glsl_optimiser": [True, False],
        "config_enable_gl_state_cache_support": [True, False],
        "config_filesystem_unicode": [True, False],
        "assert_mode": [0, 1, 2],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "resourcemanager_strict": "STRICT",
        "build_rendersystem_d3d9": True,
        "build_rendersystem_d3d11": True,
        "build_rendersystem_gl3plus": True,
        "build_rendersystem_gl": True,
        "build_rendersystem_gles2": True,
        "build_rendersystem_metal": True,
        "build_rendersystem_tiny": False,
        "build_component_paging": True,
        "build_component_meshlodgenerator": True,
        "build_component_terrain": True,
        "build_component_volume": True,
        "build_component_property": True,
        "build_component_overlay": True,
        "build_component_overlay_imgui": True,
        "build_component_bites": True,
        "build_component_bullet": True,
        "bites_static_plugins": False,
        "build_component_rtshadersystem": True,
        "build_rtshadersystem_shaders": True,
        "build_tools": False,
        "build_xsiexporter": False,
        # "build_libs_as_frameworks": True,
        "build_plugin_assimp": True,
        "build_plugin_bsp": True,
        "build_plugin_dot_scene": True,
        "build_plugin_exrcodec": True,
        "build_plugin_freeimage": False, # FIXME: set to true after https://github.com/conan-io/conan-center-index/pull/23138 is merged
        "build_plugin_octree": True,
        "build_plugin_pcz": True,
        "build_plugin_pfx": True,
        "build_plugin_stbi": True,
        "config_double": False,
        "config_node_inherit_transform": False,
        "config_threads": True,
        "config_enable_meshlod": True,
        "config_enable_dds": True,
        "config_enable_pvrtc": False,
        "config_enable_etc": True,
        "config_enable_astc": True,
        "config_enable_quad_buffer_stereo": False,
        "config_enable_viewport_orientationmode": False,
        "config_enable_gles2_glsl_optimiser": False,
        "config_enable_gl_state_cache_support": False,
        "config_filesystem_unicode": True,
        "assert_mode": 1,
    }
    options_description = {
        "resourcemanager_strict": (
            "Make ResourceManager strict for faster operation. Possible values:\n"
            "PEDANTIC - require an explicit resource group. Case sensitive lookup.\n"
            "STRICT - search in default group if not specified otherwise. Case sensitive lookup."
        ),
        "build_rendersystem_d3d9": "Build Direct3D9 RenderSystem",
        "build_rendersystem_d3d11": "Build Direct3D11 RenderSystem",
        "build_rendersystem_gl3plus": "Build OpenGL 3+ RenderSystem",
        "build_rendersystem_gl": "Build OpenGL RenderSystem",
        "build_rendersystem_gles2": "Build OpenGL ES 2.x RenderSystem",
        "build_rendersystem_metal": "Build Metal RenderSystem",
        "build_rendersystem_tiny": "Build Tiny RenderSystem (software-rendering)",
        "build_component_paging": "Build Paging component",
        "build_component_meshlodgenerator": "Build MeshLodGenerator component",
        "build_component_terrain": "Build Terrain component",
        "build_component_volume": "Build Volume component",
        "build_component_property": "Build Property component",
        "build_component_overlay": "Build Overlay component",
        "build_component_overlay_imgui": "Include dear imgui in Overlays",
        "build_component_bites": "Build OgreBites component",
        "build_component_bullet": "Build Bullet physics component",
        "bites_static_plugins": "Skip plugins.cfg and statically load plugins via OgreBites",
        "build_component_rtshadersystem": "Build RTShader System component",
        "build_rtshadersystem_shaders": "Build RTShader System FFP shaders",
        "build_tools": "Build the command-line tools",
        "build_xsiexporter": "Build the Softimage exporter",
        # "build_libs_as_frameworks": "Build frameworks for libraries on OS X.",
        "build_plugin_assimp": "Build Open Asset Import plugin",
        "build_plugin_bsp": "Build BSP SceneManager plugin",
        "build_plugin_dot_scene": "Build .scene plugin",
        "build_plugin_exrcodec": "Build EXR Codec plugin",
        "build_plugin_freeimage": "Build FreeImage codec.",
        "build_plugin_octree": "Build Octree SceneManager plugin",
        "build_plugin_pcz": "Build PCZ SceneManager plugin",
        "build_plugin_pfx": "Build ParticleFX plugin",
        "build_plugin_stbi": "Enable STBI image codec.",
        "config_double": "Use doubles instead of floats in Ogre",
        "config_node_inherit_transform": "Tells the node whether it should inherit full transform from it's parent node or derived position, orientation and scale",
        "config_threads": "Enable Ogre thread safety support for multithreading. DefaultWorkQueue is threaded if True.",
        "config_enable_meshlod": "Enable Mesh Lod.",
        "config_enable_dds": "Build DDS codec.",
        "config_enable_pvrtc": "Build PVRTC codec.",
        "config_enable_etc": "Build ETC codec.",
        "config_enable_astc": "Build ASTC codec.",
        "config_enable_quad_buffer_stereo": "Enable stereoscopic 3D support",
        "config_enable_viewport_orientationmode": "Include Viewport orientation mode support.",
        "config_enable_gles2_glsl_optimiser": "Enable GLSL optimiser use in GLES 2 render system",
        "config_enable_gl_state_cache_support": "Enable OpenGL state cache management",
        "config_filesystem_unicode": "paths expected to be in UTF-8 and wchar_t file IO routines are used",
        "assert_mode": (
            "Enable Ogre asserts and exceptions. Possible values:\n"
            "0 - Standard asserts in debug builds, nothing in release builds.\n"
            "1 - Standard asserts in debug builds, exceptions in release builds.\n"
            "2 - Exceptions in debug builds, exceptions in release builds."
        ),
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Windows":
            self.options.rm_safe("build_rendersystem_d3d9")
            self.options.rm_safe("build_rendersystem_d3d11")
        if self.settings.os == "WindowsStore":
            self.options.rm_safe("build_rendersystem_d3d9")
            self.options.rm_safe("build_rendersystem_gl3plus")
            self.options.rm_safe("build_rendersystem_gl")
            self.options.rm_safe("build_rendersystem_gles2")
        if not is_apple_os(self):
            self.options.rm_safe("build_rendersystem_metal")
            self.options.rm_safe("build_libs_as_frameworks")
        if self.settings.os == "Android":
            self.options.rm_safe("build_rendersystem_tiny")
        if self.settings.os == "WindowsStore" or (is_apple_os(self) and self.settings.os != "Macos"):
            self.options.rm_safe("build_tools")
        if not is_msvc(self):
            self.options.rm_safe("config_filesystem_unicode")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.get_safe("build_component_overlay"):
            self.options.rm_safe("build_component_overlay_imgui")
            self.options.rm_safe("build_component_bites")
        if self.options.shared or not self.options.get_safe("build_component_bites"):
            self.options.rm_safe("bites_static_plugins")
        if not self.options.get_safe("build_component_rtshadersystem"):
            self.options.rm_safe("build_rtshadersystem_shaders")
        if not self.options.get_safe("build_rendersystem_gles2"):
            self.options.rm_safe("config_enable_gles2_glsl_optimiser")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("pugixml/1.14")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zziplib/0.13.72")
        if self.options.get_safe("build_component_bites") or self.options.get_safe("build_rendersystem_tiny"):
            self.requires("sdl/2.30.7")
        if self._build_opengl:
            self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.build_component_bullet:
            self.requires("bullet3/3.25")
        if self.options.build_component_overlay:
            self.requires("freetype/2.13.2")
            if self.options.build_component_overlay_imgui:
                self.requires("imgui/1.91.0")
        if self.options.build_plugin_assimp:
            self.requires("assimp/5.4.2")
        if self.options.build_plugin_exrcodec:
            # OpenEXR 3.x is not compatible
            self.requires("openexr/2.5.7")
        if self.options.build_plugin_freeimage:
            self.requires("freeimage/3.18.0")

        # TODO: OpenMP for RenderSystem_Tiny
        # TODO: unvendor stb in Plugin_STBI

    @property
    def _build_opengl(self):
        # https://github.com/OGRECave/ogre/blob/v14.2.4/RenderSystems/CMakeLists.txt#L32-L34
        return (self.options.get_safe("build_rendersystem_gl") or
                self.options.get_safe("build_rendersystem_gles2") or
                self.options.get_safe("build_rendersystem_gl3plus"))

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

        # https://github.com/OGRECave/ogre/blob/v14.2.4/CMake/ConfigureBuild.cmake#L21-L25
        if self.options.shared and is_apple_os(self) and self.settings.os != "Macos":
            raise ConanInvalidConfiguration(f"OGRE shared library is not available on {self.settings.os}")

        if self.options.config_enable_gl_state_cache_support and not self._build_opengl:
            raise ConanInvalidConfiguration("config_enable_gl_state_cache_support requires GL, GLES2 or GL3PLUS RenderSystem")

        def _missing_dep_warning(opt, dep):
            if self.options.get_safe(opt):
                self.output.warning(f"{opt} requires {dep}, which is not available in Conan Center Index. "
                                    "Assuming it is provided by the system.")

        _missing_dep_warning("config_enable_quad_buffer_stereo", "NVAPI")
        _missing_dep_warning("build_xsiexporter", "Softimage")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        # https://github.com/OGRECave/ogre/blob/v14.2.4/CMakeLists.txt#L281-L420
        tc.variables["OGRE_STATIC"] = not self.options.shared
        tc.variables["OGRE_RESOURCEMANAGER_STRICT"] = 2 if self.options.resourcemanager_strict == "STRICT" else 1
        tc.variables["OGRE_BUILD_RENDERSYSTEM_D3D9"] = self.options.get_safe("build_rendersystem_d3d9", False)
        tc.variables["OGRE_BUILD_RENDERSYSTEM_D3D11"] = self.options.get_safe("build_rendersystem_d3d11", False)
        tc.variables["OGRE_BUILD_RENDERSYSTEM_GL3PLUS"] = self.options.get_safe("build_rendersystem_gl3plus", False)
        tc.variables["OGRE_BUILD_RENDERSYSTEM_GL"] = self.options.get_safe("build_rendersystem_gl", False)
        tc.variables["OGRE_BUILD_RENDERSYSTEM_GLES2"] = self.options.get_safe("build_rendersystem_gles2", False)
        tc.variables["OGRE_BUILD_RENDERSYSTEM_METAL"] = self.options.get_safe("build_rendersystem_metal", False)
        tc.variables["OGRE_BUILD_RENDERSYSTEM_TINY"] = self.options.get_safe("build_rendersystem_tiny", False)
        tc.variables["OGRE_BUILD_COMPONENT_PAGING"] = self.options.build_component_paging
        tc.variables["OGRE_BUILD_COMPONENT_MESHLODGENERATOR"] = self.options.build_component_meshlodgenerator
        tc.variables["OGRE_BUILD_COMPONENT_TERRAIN"] = self.options.build_component_terrain
        tc.variables["OGRE_BUILD_COMPONENT_VOLUME"] = self.options.build_component_volume
        tc.variables["OGRE_BUILD_COMPONENT_PROPERTY"] = self.options.build_component_property
        tc.variables["OGRE_BUILD_COMPONENT_OVERLAY"] = self.options.build_component_overlay
        tc.variables["OGRE_BUILD_COMPONENT_OVERLAY_IMGUI"] = self.options.get_safe("build_component_overlay_imgui", False)
        tc.variables["OGRE_BUILD_COMPONENT_BITES"] = self.options.get_safe("build_component_bites", False)
        tc.variables["OGRE_BUILD_COMPONENT_BULLET"] = self.options.build_component_bullet
        tc.variables["OGRE_BITES_STATIC_PLUGINS"] = self.options.get_safe("bites_static_plugins", False)
        tc.variables["OGRE_BUILD_COMPONENT_PYTHON"] = False
        tc.variables["OGRE_BUILD_COMPONENT_JAVA"] = False
        tc.variables["OGRE_BUILD_COMPONENT_CSHARP"] = False
        tc.variables["OGRE_BUILD_COMPONENT_RTSHADERSYSTEM"] = self.options.build_component_rtshadersystem
        tc.variables["OGRE_BUILD_RTSHADERSYSTEM_SHADERS"] = self.options.get_safe("build_rtshadersystem_shaders", False)
        tc.variables["OGRE_BUILD_SAMPLES"] = False
        tc.variables["OGRE_BUILD_TOOLS"] = self.options.get_safe("build_tools", False)
        tc.variables["OGRE_BUILD_XSIEXPORTER"] = self.options.get_safe("build_xsiexporter", False)
        tc.variables["OGRE_BUILD_LIBS_AS_FRAMEWORKS"] = False  # TODO: requires additional package_info() logic
        tc.variables["OGRE_BUILD_TESTS"] = False
        tc.variables["OGRE_BUILD_PLUGIN_ASSIMP"] = self.options.build_plugin_assimp
        tc.variables["OGRE_BUILD_PLUGIN_BSP"] = self.options.build_plugin_bsp
        tc.variables["OGRE_BUILD_PLUGIN_GLSLANG"] = False  # TODO
        tc.variables["OGRE_BUILD_PLUGIN_OCTREE"] = self.options.build_plugin_octree
        tc.variables["OGRE_BUILD_PLUGIN_PFX"] = self.options.build_plugin_pfx
        tc.variables["OGRE_BUILD_PLUGIN_DOT_SCENE"] = self.options.build_plugin_dot_scene
        tc.variables["OGRE_BUILD_PLUGIN_PCZ"] = self.options.build_plugin_pcz
        tc.variables["OGRE_BUILD_PLUGIN_CG"] = False  # Cg is legacy and not worth adding support for on CCI, most likely
        tc.variables["OGRE_BUILD_PLUGIN_EXRCODEC"] = self.options.build_plugin_exrcodec
        tc.variables["OGRE_BUILD_PLUGIN_RSIMAGE"] = False  # Requires Rust support on CCI
        tc.variables["OGRE_BUILD_PLUGIN_STBI"] = self.options.build_plugin_stbi
        tc.variables["OGRE_CONFIG_DOUBLE"] = self.options.config_double
        tc.variables["OGRE_CONFIG_NODE_INHERIT_TRANSFORM"] = self.options.config_node_inherit_transform
        tc.variables["OGRE_CONFIG_THREADS"] = "3" if self.options.config_threads else "0"
        tc.variables["OGRE_CONFIG_ENABLE_MESHLOD"] = self.options.config_enable_meshlod
        tc.variables["OGRE_CONFIG_ENABLE_DDS"] = self.options.config_enable_dds
        tc.variables["OGRE_CONFIG_ENABLE_PVRTC"] = self.options.config_enable_pvrtc
        tc.variables["OGRE_CONFIG_ENABLE_ETC"] = self.options.config_enable_etc
        tc.variables["OGRE_CONFIG_ENABLE_ASTC"] = self.options.config_enable_astc
        tc.variables["OGRE_CONFIG_ENABLE_QUAD_BUFFER_STEREO"] = self.options.get_safe("config_enable_quad_buffer_stereo", False)
        tc.variables["OGRE_CONFIG_ENABLE_ZIP"] = True
        tc.variables["OGRE_CONFIG_ENABLE_VIEWPORT_ORIENTATIONMODE"] = self.options.config_enable_viewport_orientationmode
        tc.variables["OGRE_CONFIG_ENABLE_GLES2_CG_SUPPORT"] = False
        tc.variables["OGRE_CONFIG_ENABLE_GLES2_GLSL_OPTIMISER"] = self.options.get_safe("config_enable_gles2_glsl_optimiser", False)
        tc.variables["OGRE_CONFIG_ENABLE_GL_STATE_CACHE_SUPPORT"] = self.options.get_safe("config_enable_gl_state_cache_support", False)
        tc.variables["OGRE_CONFIG_FILESYSTEM_UNICODE"] = self.options.get_safe("config_filesystem_unicode", False)
        tc.variables["OGRE_CONFIG_STATIC_LINK_CRT"] = is_msvc_static_runtime(self)
        tc.variables["OGRE_INSTALL_SAMPLES"] = False
        tc.variables["OGRE_INSTALL_TOOLS"] = self.options.get_safe("build_tools", False)
        tc.variables["OGRE_INSTALL_DOCS"] = False
        tc.variables["OGRE_INSTALL_PDB"] = False
        tc.variables["OGRE_PROFILING"] = False
        tc.variables["OGRE_LIB_DIRECTORY"] = "lib"
        tc.variables["OGRE_BIN_DIRECTORY"] = "bin"
        tc.variables["OGRE_INSTALL_VSPROPS"] = False
        # https://github.com/OGRECave/ogre/blob/v14.2.4/CMake/ConfigureBuild.cmake#L63-L69
        tc.variables["OGRE_ASSERT_MODE"] = self.options.assert_mode
        tc.variables["OGRE_BUILD_DEPENDENCIES"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("openexr", "cmake_file_name", "OpenEXR")
        deps.set_property("freeimage", "cmake_file_name", "FreeImage")
        deps.set_property("freetype", "cmake_file_name", "Freetype")
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "PlugIns", "Assimp", "CMakeLists.txt"),
                        "fix::assimp", "assimp::assimp")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    @property
    def _ogre_cmake_packages(self):
        return ["Cg", "DirectX", "DirectX11", "Softimage", "GLSLOptimizer", "HLSL2GLSL"]

    def _create_cmake_module_variables(self, module_file, version):
        content = textwrap.dedent(f"""\
            set(OGRE_PREFIX_DIR ${{CMAKE_CURRENT_LIST_DIR}}/../..)
            set(OGRE{version.major}_VERSION_MAJOR {version.major})
            set(OGRE{version.major}_VERSION_MINOR {version.minor})
            set(OGRE{version.major}_VERSION_PATCH {version.patch})
            set(OGRE{version.major}_VERSION_STRING "{version.major}.{version.minor}.{version.patch}")

            set(OGRE_MEDIA_DIR "${{OGRE_PREFIX_DIR}}/share/OGRE/Media")
            set(OGRE_PLUGIN_DIR "${{OGRE_PREFIX_DIR}}/lib/OGRE")
            set(OGRE_CONFIG_DIR "${{OGRE_PREFIX_DIR}}/share/OGRE")
        """)
        # Some hacky dependency resolution for packages that are not available from Conan
        for pkg in self._ogre_cmake_packages:
            content += textwrap.dedent(f"""\
                find_package({pkg} MODULE QUIET)
                if({pkg}_FOUND OR {pkg.upper()}_FOUND)
                    target_link_libraries(OGRE::OgreMain INTERFACE ${{{pkg}}}_LIBRARIES}} ${{{pkg.upper()}}}_LIBRARIES}})
                    target_include_directories(OGRE::OgreMain INTERFACE ${{{pkg}}}_INCLUDE_DIRS}} ${{{pkg.upper()}}}_INCLUDE_DIRS}})
                endif()
            """)
        save(self, module_file, content)

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "License.md",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "Docs"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "OGRE", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake", "OGRE"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path), Version(self.version)
        )
        # Include modules for packages that are not available from Conan
        for pkg in self._ogre_cmake_packages:
            copy(self, f"Find{pkg}.cmake",
                 src=os.path.join(self.source_folder, "CMake", "Packages"),
                 dst=os.path.join(self.package_folder, self._module_file_rel_dir))
            copy(self, "FindPkgMacros.cmake",
                 src=os.path.join(self.source_folder, "CMake", "Utils"),
                 dst=os.path.join(self.package_folder, self._module_file_rel_dir))

    @property
    def _module_file_rel_dir(self):
        return os.path.join("lib", "cmake", "OGRE")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_file_rel_dir, f"conan-official-{self.name}-variables.cmake")

    def _format_lib(self, lib):
        # https://github.com/OGRECave/ogre/blob/v14.2.4/CMake/ConfigureBuild.cmake#L140-L145
        if not self.options.shared:
            lib += "Static"
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            lib += "_d"
        return lib

    @property
    def _shared_extension(self):
        if self.settings.os == "Windows":
            return ".dll"
        elif is_apple_os(self):
            return ".dylib"
        else:
            return ".so"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OGRE")
        self.cpp_info.set_property("cmake_target_name", "OGRE::OGRE")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])

        include_prefix = os.path.join("include", "OGRE")
        plugin_lib_dir = os.path.join("lib", "OGRE")

        def _add_component(comp, *, requires=None, libs=None, includedirs=None, libdirs=None, cmake_target=None, pkg_config_name=None):
            self.cpp_info.components[comp].set_property("cmake_target_name", cmake_target)
            self.cpp_info.components[comp].set_property("pkg_config_name", pkg_config_name)
            if comp != "OgreMain":
                self.cpp_info.components[comp].requires = ["OgreMain"]
            self.cpp_info.components[comp].requires += requires or []
            self.cpp_info.components[comp].libs = [self._format_lib(lib) for lib in (libs or [])]
            self.cpp_info.components[comp].includedirs = includedirs or []
            self.cpp_info.components[comp].libdirs = libdirs or []
            self.cpp_info.components[comp].builddirs.append(self._module_file_rel_dir)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components[comp].system_libs.append("pthread")

            # TODO: Legacy, to be removed on Conan 2.0
            self.cpp_info.components[comp].names["cmake_find_package"] = comp
            self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
            self.cpp_info.components[comp].names["cmake_paths"] = comp
            self.cpp_info.components[comp].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components[comp].build_modules["cmake_paths"] = [self._module_file_rel_path]

        def _add_core_component(comp, *, requires=None):
            _add_component(
                comp,
                cmake_target=f"OGRE::{comp}",
                pkg_config_name=f"OGRE-{comp}",
                libs=[f"Ogre{comp}"],
                libdirs=["lib"],
                includedirs=["include", include_prefix, os.path.join(include_prefix, comp)],
                requires=requires,
            )

        def _add_plugin_component(comp, *, requires=None, extra_libs=None):
            if comp.startswith("Codec_"):
                dirname = f"{comp.replace('Codec_', '')}Codec"
            else:
                dirname = comp.replace("Plugin_", "")
            _add_component(
                comp,
                cmake_target=None,
                pkg_config_name=None,
                # Adding the extension for a full name since the plugin libs don't include the standard 'lib' prefix
                libs=[comp + self._shared_extension] + (extra_libs or []),
                libdirs=[plugin_lib_dir],
                includedirs=["include", include_prefix, os.path.join(include_prefix, "Plugins", dirname)],
                requires=requires,
            )

        def _add_rendersystem_component(comp, *, requires=None, extra_libs=None):
            dirname = comp.replace("RenderSystem_", "")
            _add_component(
                comp,
                cmake_target=None,
                pkg_config_name=None,
                libs=[comp + self._shared_extension] + (extra_libs or []),
                libdirs=[plugin_lib_dir],
                includedirs=["include", include_prefix, os.path.join(include_prefix, "RenderSystems", dirname)],
                requires=requires,
            )

        _add_component(
            "OgreMain",
            cmake_target="OGRE::OgreMain",
            pkg_config_name="OGRE",
            libs=["OgreMain"],
            libdirs=["lib"],
            includedirs=["include", include_prefix],
            requires=["pugixml::pugixml", "zlib::zlib", "zziplib::zziplib"],
        )

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["OgreMain"].requires.append("xorg::xorg")

        if self.options.get_safe("build_component_bites"):
            _add_core_component("Bites", requires=["Overlay", "sdl::sdl"])
        if self.options.get_safe("build_component_bullet"):
            _add_core_component("Bullet", requires=["bullet3::bullet3"])
        if self.options.build_component_meshlodgenerator:
            _add_core_component("MeshLodGenerator")
        if self.options.build_component_overlay:
            _add_core_component("Overlay", requires=["freetype::freetype"])
            if self.options.get_safe("build_component_overlay_imgui"):
                self.cpp_info.components["Overlay"].requires.append("imgui::imgui")
        if self.options.build_component_paging:
            _add_core_component("Paging")
        if self.options.build_component_property:
            _add_core_component("Property")
        if self.options.build_component_rtshadersystem:
            _add_core_component("RTShaderSystem")
        if self.options.build_component_terrain:
            _add_core_component("Terrain")
        if self.options.build_component_volume:
            _add_core_component("Volume")

        if self._build_opengl:
            if not self.options.shared:
                _add_core_component("GLSupport", requires=["opengl::opengl"])
            else:
                self.cpp_info.components["OgreMain"].requires.append("opengl::opengl")

        if self.options.build_plugin_assimp:
            _add_plugin_component("Codec_Assimp", requires=["assimp::assimp"])
        if self.options.build_plugin_bsp:
            _add_plugin_component("Plugin_BSPSceneManager")
        if self.options.build_plugin_dot_scene:
            _add_plugin_component("Plugin_DotScene", requires=["pugixml::pugixml"])
        if self.options.build_plugin_exrcodec:
            _add_plugin_component("Codec_EXR", requires=["openexr::openexr"])
        if self.options.build_plugin_freeimage:
            _add_plugin_component("Codec_FreeImage", requires=["freeimage::freeimage"])
        if self.options.build_plugin_octree:
            _add_plugin_component("Plugin_OctreeSceneManager")
        if self.options.build_plugin_pcz:
            _add_plugin_component("Plugin_PCZSceneManager")
            _add_plugin_component("Plugin_OctreeZone", requires=["Plugin_PCZSceneManager"])
        if self.options.build_plugin_pfx:
            _add_plugin_component("Plugin_ParticleFX")
        if self.options.build_plugin_stbi:
            _add_plugin_component("Codec_STBI")

        if self.options.get_safe("build_rendersystem_d3d9"):
            _add_rendersystem_component("RenderSystem_Direct3D9")
            # https://github.com/OGRECave/ogre/blob/v14.2.6/CMake/Packages/FindDirectX.cmake#L58-L60
            self.cpp_info.components["RenderSystem_Direct3D9"].system_libs += ["d3d9", "d3dx9", "dxguid"]
        if self.options.get_safe("build_rendersystem_d3d11"):
            _add_rendersystem_component("RenderSystem_Direct3D11")
            if self.settings.compiler == "gcc":
                self.cpp_info.components["RenderSystem_Direct3D11"].system_libs += ["psapi", "d3dcompiler"]
            # https://github.com/OGRECave/ogre/blob/v14.2.6/CMake/Packages/FindDirectX11.cmake#L95-L100
            self.cpp_info.components["RenderSystem_Direct3D11"].system_libs += ["dxerr", "dxguid", "dxgi", "d3dcompiler", "d3d11", "d3dx11"]
        if self.options.get_safe("build_rendersystem_gl"):
            _add_rendersystem_component("RenderSystem_GL", requires=["opengl::opengl"])
        if self.options.get_safe("build_rendersystem_gl3plus"):
            _add_rendersystem_component("RenderSystem_GL3Plus", requires=["opengl::opengl"])
        if self.options.get_safe("build_rendersystem_gles2"):
            _add_rendersystem_component("RenderSystem_GLES2", requires=["opengl::opengl"])
        if self.options.get_safe("build_rendersystem_metal"):
            _add_rendersystem_component("RenderSystem_Metal")
            if self.settings.os == "iOS":
                self.cpp_info.components["RenderSystem_Metal"].frameworks += ["Metal", "QuartzCore"]
            else:
                self.cpp_info.components["RenderSystem_Metal"].frameworks += ["Metal", "AppKit", "QuartzCore"]
        if self.options.get_safe("build_rendersystem_tiny"):
            _add_rendersystem_component("RenderSystem_Tiny", requires=["sdl::sdl"])

        # TODO: Legacy, to be removed on Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "OGRE"
        self.cpp_info.names["cmake_find_package_multi"] = "OGRE"
        self.cpp_info.names["cmake_paths"] = "OGRE"
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
