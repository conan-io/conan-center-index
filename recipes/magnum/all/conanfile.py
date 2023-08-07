# TODO: verify the Conan v2 migration

import os

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.android import android_abi
from conan.tools.apple import XCRun, fix_apple_shared_install_name, is_apple_os, to_apple_arch
from conan.tools.build import build_jobs, can_run, check_min_cppstd, cross_building, default_cppstd, stdcpp_library, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches,
    chdir,
    collect_libs,
    copy,
    download,
    export_conandata_patches,
    get,
    load,
    mkdir,
    patch,
    patches,
    rename,
    replace_in_file,
    rm,
    rmdir,
    save,
    symlinks,
    unzip,
)
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfig, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import (
    MSBuild,
    MSBuildDeps,
    MSBuildToolchain,
    NMakeDeps,
    NMakeToolchain,
    VCVars,
    check_min_vs,
    is_msvc,
    is_msvc_static_runtime,
    msvc_runtime_flag,
    unix_path,
    unix_path_package_info_legacy,
    vs_layout,
)
from conan.tools.scm import Version
from conan.tools.system import package_manager
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import functools
import os
import re
import textwrap

required_conan_version = ">=1.53.0"


class MagnumConan(ConanFile):
    name = "magnum"
    description = "Lightweight and modular C++11/C++14 graphics middleware for games and data visualization"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"
    topics = ("magnum", "graphics", "middleware", "graphics", "rendering", "gamedev", "opengl", "3d", "2d", "opengl", "game-engine", "pre-built")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "shared_plugins": [True, False],
        # Follow documented build-options in https://doc.magnum.graphics/magnum/building.html#building-features
        #   Options like `with_xxxx` have been renamed to `xxxx`
        #   Options related to GL are being refactored into a choice option: gles2, gles3 or desktop_gl
        #   Some documented options are not available in sources: with_shaderstools, vk_info, with_shaderconverter and with_anyshaderconverter
        #   Option names are converted to snake_case
        "target_gl": ["gles2", "gles3", "desktop_gl", False],
        "target_headless": [True, False],
        "target_vk": [True, False],
        "audio": [True, False],
        "debug_tools": [True, False],
        "gl": [True, False],
        "mesh_tools": [True, False],
        "primitives": [True, False],
        "scene_graph": [True, False],
        "shaders": [True, False],
        "text": [True, False],
        "texture_tools": [True, False],
        "trade": [True, False],
        "vk": [True, False],
        "android_application": [True, False],
        "emscripten_application": [True, False],
        "glfw_application": [True, False],
        "glx_application": [True, False],
        "sdl2_application": [True, False],
        "xegl_application": [True, False],
        "windowless_cgl_application": [True, False],
        "windowless_egl_application": [True, False],
        "windowless_glx_application": [True, False],
        "windowless_ios_application": [True, False],
        "windowless_wgl_application": [True, False],
        "windowless_windows_egl_application": [True, False],
        "cgl_context": [True, False],
        "egl_context": [True, False],
        "glx_context": [True, False],
        "wgl_context": [True, False],
        "gl_info": [True, False],
        "al_info": [True, False],
        "distance_field_converter": [True, False],
        "font_converter": [True, False],
        "image_converter": [True, False],
        "scene_converter": [True, False],
        # Plugins
        "any_audio_importer": [True, False],
        "any_image_converter": [True, False],
        "any_image_importer": [True, False],
        "any_scene_converter": [True, False],
        "any_scene_importer": [True, False],
        "magnum_font": [True, False],
        "magnum_font_converter": [True, False],
        "obj_importer": [True, False],
        "tga_importer": [True, False],
        "tga_image_converter": [True, False],
        "wav_audio_importer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "shared_plugins": True,
        "target_gl": "desktop_gl",
        "target_headless": True,
        "target_vk": True,
        "audio": True,
        "debug_tools": True,
        "gl": True,
        "mesh_tools": True,
        "primitives": True,
        "scene_graph": True,
        "shaders": True,
        "text": True,
        "texture_tools": True,
        "trade": True,
        "vk": True,
        "android_application": True,
        "emscripten_application": True,
        "glfw_application": True,
        "glx_application": True,
        "sdl2_application": True,
        "xegl_application": True,
        "windowless_cgl_application": True,
        "windowless_egl_application": True,
        "windowless_glx_application": True,
        "windowless_ios_application": True,
        "windowless_wgl_application": True,
        "windowless_windows_egl_application": True,
        "cgl_context": True,
        "egl_context": True,
        "glx_context": True,
        "wgl_context": True,
        "gl_info": True,
        "al_info": True,
        "distance_field_converter": True,
        "font_converter": True,
        "image_converter": True,
        "scene_converter": True,
        # Plugins
        "any_audio_importer": True,
        "any_image_converter": True,
        "any_image_importer": True,
        "any_scene_converter": True,
        "any_scene_importer": True,
        "magnum_font": True,
        "magnum_font_converter": True,
        "obj_importer": True,
        "tga_importer": True,
        "tga_image_converter": True,
        "wav_audio_importer": True,
    }

    def export_sources(self):
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        # Doc says that 'distance_field_converter' is only available with "desktop GL" (the same is said for 'font_converter', but it builds)
        # TODO: Here we probably have a CHOICE OPTION
        if self.options.target_gl in ["gles2", "gles3"]:
            self.options.rm_safe("distance_field_converter")

        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("egl_context")
            self.options.rm_safe("xegl_application")
            self.options.rm_safe("windowless_egl_application")
            self.options.rm_safe("windowless_ios_application")
            self.options.rm_safe("windowless_glx_application")
            self.options.rm_safe("windowless_windows_egl_application")  # requires ANGLE
            self.options.rm_safe("target_headless")  # Requires EGL (when used gl_info)
            self.options.rm_safe("glx_application")
            self.options.rm_safe("cgl_context")
            self.options.rm_safe("windowless_cgl_application")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.options.rm_safe("cgl_context")
            self.options.rm_safe("windowless_cgl_application")
            self.options.rm_safe("wgl_context")
            self.options.rm_safe("windowless_wgl_application")
            self.options.rm_safe("windowless_windows_egl_application")

        if self.settings.os == "Macos":
            self.options.rm_safe("egl_context")
            self.options.rm_safe("glx_application")  # Requires GL/glx.h (maybe XQuartz project)
            self.options.rm_safe("xegl_application")
            self.options.rm_safe("windowless_egl_application")
            self.options.rm_safe("windowless_glx_application")  # Requires GL/glx.h (maybe XQuartz project)
            self.options.rm_safe("windowless_wgl_application")
            self.options.rm_safe("windowless_windows_egl_application")
            self.options.rm_safe("target_headless")  # Requires EGL (when used gl_info)

        if self.settings.os != "Android":
            self.options.rm_safe("android_application")

        if self.settings.os != "Emscripten":
            self.options.rm_safe("emscripten_application")

        if self.settings.os != "iOS":
            self.options.rm_safe("windowless_ios_application")

    @property
    def _executables(self):
        # (executable, option name)
        all_execs = [
            ("gl-info", "gl_info"),
            ("al-info", "al_info"),
            ("distancefieldconverter", "distance_field_converter"),
            ("fontconverter", "font_converter"),
            ("imageconverter", "image_converter"),
            ("sceneconverter", "scene_converter"),
        ]
        return [executable for executable, opt_name in all_execs if self.options.get_safe(opt_name)]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"corrade/{self.version}")
        if self.options.audio:
            self.requires("openal/1.22.2")
        if self.options.gl:
            self.requires("opengl/system")
        if self.options.vk:
            self.requires("vulkan-loader/1.3.243.0")

        if (
            self.options.get_safe("egl_context", False)
            or self.options.get_safe("xegl_application", False)
            or self.options.get_safe("windowless_egl_application", False)
            or self.options.get_safe("windowless_ios_application")
            or self.options.get_safe("windowless_windows_egl_application", False)
            or self.options.get_safe("target_headless", False)
        ):
            self.requires("egl/system")

        if self.options.glfw_application:
            self.requires("glfw/3.3.8")

        if self.options.sdl2_application:
            self.requires("sdl/2.28.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5.0":
            raise ConanInvalidConfiguration("GCC older than 5 is not supported (missing C++11 features)")

        if self.options.shared and not self.dependencies["corrade"].options.shared:
            # To fix issue with resource management, see here: https://github.com/mosra/magnum/issues/304#issuecomment-451768389
            raise ConanInvalidConfiguration("If using 'shared=True', corrade should be shared as well")

        if not self.options.gl and (self.options.target_gl or self.options.get_safe("target_headless", False)):
            raise ConanInvalidConfiguration("Option 'gl=True' is required")

        if self.options.target_gl in ["gles2", "gles3"] and is_apple_os(self):
            raise ConanInvalidConfiguration("OpenGL ES is not supported in Macos")

        if self.options.target_gl in ["gles2", "gles3"] and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenGL ES is not supported in Windows")

        if not self.options.vk and self.options.target_vk:
            raise ConanInvalidConfiguration("Option 'vk=True' is required")

        if self.options.get_safe("cgl_context", False) and not self.options.target_gl:
            raise ConanInvalidConfiguration("Option 'cgl_context' requires some 'target_gl'")

        if self.options.get_safe("windowless_cgl_application", False) and not self.options.target_gl:
            raise ConanInvalidConfiguration("Option 'windowless_cgl_application' requires some 'target_gl'")

        if self.options.al_info and not self.options.audio:
            raise ConanInvalidConfiguration("Option 'al_info' requires 'audio=True'")

        if self.options.magnum_font_converter and not self.options.tga_image_converter:
            raise ConanInvalidConfiguration("magnum_font_converter requires tga_image_converter")

    def build_requirements(self):
        self.tool_requires(f"corrade/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DEPRECATED"] = False
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        # tc.variables["BUILD_STATIC_UNIQUE_GLOBALS"]
        tc.variables["BUILD_PLUGINS_STATIC"] = not self.options.shared_plugins
        tc.variables["LIB_SUFFIX"] = ""
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_GL_TESTS"] = False
        tc.variables["BUILD_AL_TESTS"] = False
        tc.variables["WITH_OPENGLTESTER"] = False
        tc.variables["WITH_VULKANTESTER"] = False

        tc.variables["TARGET_GL"] = bool(self.options.target_gl)
        tc.variables["TARGET_GLES"] = self.options.target_gl == "gles3"
        tc.variables["TARGET_GLES2"] = self.options.target_gl == "gles2"
        tc.variables["TARGET_DESKTOP_GLES"] = self.options.target_gl == "desktop_gl"
        tc.variables["TARGET_HEADLESS"] = self.options.get_safe("target_headless", False)
        tc.variables["TARGET_VK"] = self.options.target_vk

        tc.variables["WITH_AUDIO"] = self.options.audio
        tc.variables["WITH_DEBUGTOOLS"] = self.options.debug_tools
        tc.variables["WITH_GL"] = self.options.gl
        tc.variables["WITH_MESHTOOLS"] = self.options.mesh_tools
        tc.variables["WITH_PRIMITIVES"] = self.options.primitives
        tc.variables["WITH_SCENEGRAPH"] = self.options.scene_graph
        tc.variables["WITH_SHADERS"] = self.options.shaders
        tc.variables["WITH_TEXT"] = self.options.text
        tc.variables["WITH_TEXTURETOOLS"] = self.options.texture_tools
        tc.variables["WITH_TRADE"] = self.options.trade
        tc.variables["WITH_VK"] = self.options.vk

        tc.variables["WITH_ANDROIDAPPLICATION"] = self.options.get_safe("android_application", False)
        tc.variables["WITH_EMSCRIPTENAPPLICATION"] = self.options.get_safe("emscripten_application", False)
        tc.variables["WITH_GLFWAPPLICATION"] = self.options.glfw_application
        tc.variables["WITH_GLXAPPLICATION"] = self.options.get_safe("glx_application", False)
        tc.variables["WITH_SDL2APPLICATION"] = self.options.sdl2_application
        tc.variables["WITH_XEGLAPPLICATION"] = self.options.get_safe("xegl_application", False)
        tc.variables["WITH_WINDOWLESSCGLAPPLICATION"] = self.options.get_safe("windowless_cgl_application", False)
        tc.variables["WITH_WINDOWLESSEGLAPPLICATION"] = self.options.get_safe("windowless_egl_application", False)
        tc.variables["WITH_WINDOWLESSGLXAPPLICATION"] = self.options.get_safe("windowless_glx_application", False)
        tc.variables["WITH_WINDOWLESSIOSAPPLICATION"] = self.options.get_safe("windowless_ios_application", False)
        tc.variables["WITH_WINDOWLESSWGLAPPLICATION"] = self.options.get_safe("windowless_wgl_application", False)
        tc.variables["WITH_WINDOWLESSWINDOWSEGLAPPLICATION"] = self.options.get_safe("windowless_windows_egl_application", False)

        tc.variables["WITH_CGLCONTEXT"] = self.options.get_safe("cgl_context", False)
        tc.variables["WITH_EGLCONTEXT"] = self.options.get_safe("egl_context", False)
        tc.variables["WITH_GLXCONTEXT"] = self.options.glx_context
        tc.variables["WITH_WGLCONTEXT"] = self.options.get_safe("wgl_context", False)

        ##### Plugins related #####
        tc.variables["WITH_ANYAUDIOIMPORTER"] = self.options.any_audio_importer
        tc.variables["WITH_ANYIMAGECONVERTER"] = self.options.any_image_converter
        tc.variables["WITH_ANYIMAGEIMPORTER"] = self.options.any_image_importer
        tc.variables["WITH_ANYSCENECONVERTER"] = self.options.any_scene_converter
        tc.variables["WITH_ANYSCENEIMPORTER"] = self.options.any_scene_importer
        tc.variables["WITH_MAGNUMFONT"] = self.options.magnum_font
        tc.variables["WITH_MAGNUMFONTCONVERTER"] = self.options.magnum_font_converter
        tc.variables["WITH_OBJIMPORTER"] = self.options.obj_importer
        tc.variables["WITH_TGAIMPORTER"] = self.options.tga_importer
        tc.variables["WITH_TGAIMAGECONVERTER"] = self.options.tga_image_converter
        tc.variables["WITH_WAVAUDIOIMPORTER"] = self.options.wav_audio_importer

        #### Command line utilities ####
        tc.variables["WITH_GL_INFO"] = self.options.gl_info
        tc.variables["WITH_AL_INFO"] = self.options.al_info
        tc.variables["WITH_DISTANCEFIELDCONVERTER"] = self.options.get_safe("distance_field_converter", False)
        tc.variables["WITH_FONTCONVERTER"] = self.options.font_converter
        tc.variables["WITH_IMAGECONVERTER"] = self.options.image_converter
        tc.variables["WITH_SCENECONVERTER"] = self.options.scene_converter

        tc.generate()

        tc = CMakeDeps(self)
        tc.set_property("glfw", "cmake_file_name", "GLFW")
        tc.set_property("glfw", "cmake_target_name", "GLFW::GLFW")
        tc.set_property("glfw", "cmake_target_aliases", ["glfw"])
        tc.set_property("egl", "cmake_file_name", "EGL")
        tc.set_property("egl", "cmake_target_name", "EGL::EGL")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})', "")
        # Get rid of cmake_dependent_option, it can activate features when we try to disable them,
        #   let the Conan user decide what to use and what not.
        with open(os.path.join(self.source_folder, "CMakeLists.txt"), "r+", encoding="utf-8") as f:
            text = f.read()
            text = re.sub(r"cmake_dependent_option(([0-9A-Z_]+) .*)", r'option(\1 "Option \1 disabled by Conan" OFF)', text)
            f.seek(0)
            f.write(text)
            f.truncate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        build_modules_folder = os.path.join(self.package_folder, "lib", "cmake")
        os.makedirs(build_modules_folder)
        for executable in self._executables:
            build_module_path = os.path.join(build_modules_folder, f"conan-magnum-{executable}.cmake")
            save(self, build_module_path, encoding="utf-8", content=textwrap.dedent(f"""\
                if(NOT TARGET Magnum::{executable})
                    if(CMAKE_CROSSCOMPILING)
                        find_program(MAGNUM_EXEC_PROGRAM magnum-{executable} PATHS ENV PATH NO_DEFAULT_PATH)
                    endif()
                    if(NOT MAGNUM_EXEC_PROGRAM)
                        set(MAGNUM_EXEC_PROGRAM "${{CMAKE_CURRENT_LIST_DIR}}/../../bin/magnum-{executable}")
                    endif()
                    get_filename_component(MAGNUM_EXEC_PROGRAM "${{MAGNUM_EXEC_PROGRAM}}" ABSOLUTE)
                    add_executable(Magnum::{executable} IMPORTED)
                    set_property(TARGET Magnum::{executable} PROPERTY IMPORTED_LOCATION ${{MAGNUM_EXEC_PROGRAM}})
                endif()
            """))

        if not self.options.shared_plugins:
            for component, target, library, _, _ in self._plugins:
                build_module_path = os.path.join(build_modules_folder, f"conan-magnum-plugins-{component}.cmake")
                save(self, encoding="utf-8", content=textwrap.dedent(f"""\
                    if(NOT ${{CMAKE_VERSION}} VERSION_LESS "3.0")
                        if(TARGET Magnum::{target})
                            set_target_properties(Magnum::{target} PROPERTIES INTERFACE_SOURCES
                                                "${{CMAKE_CURRENT_LIST_DIR}}/../../include/MagnumPlugins/{library}/importStaticPlugin.cpp")
                        endif()
                    endif()
                """))

        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "*.cmake", src=os.path.join(self.export_sources_folder, "cmake"), dst=os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Magnum")
        self.cpp_info.set_property("cmake_target_name", "Magnum::Magnum")
        self.cpp_info.names["cmake_find_package"] = "Magnum"
        self.cpp_info.names["cmake_find_package_multi"] = "Magnum"

        magnum_plugin_libdir = "magnum-d" if self.settings.build_type == "Debug" and self.options.shared_plugins else "magnum"
        plugin_lib_suffix = "-d" if self.settings.build_type == "Debug" and not self.options.shared_plugins else ""
        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""

        def _add_component(component_name, lib_name, requires):
            component = self.cpp_info.components[component_name]
            component.set_property("cmake_target_name", f"Magnum::{lib_name}")
            component.names["cmake_find_package"] = lib_name
            component.names["cmake_find_package_multi"] = lib_name
            component.libs = [f"Magnum{lib_name}{lib_suffix}"]
            component.requires = requires

        build_modules = []

        def _add_cmake_module(component, module_name):
            cmake_mod = os.path.join("lib", "cmake", module_name)
            build_modules.append(cmake_mod)
            self.cpp_info.components[component].set_property("cmake_build_modules", [cmake_mod])
            self.cpp_info.components[component].build_modules["cmake_find_package"].append(cmake_mod)
            self.cpp_info.components[component].build_modules["cmake_find_package_multi"].append(cmake_mod)

        # The FindMagnum.cmake file provided by the library populates some extra stuff
        _add_cmake_module("_magnum", "conan-magnum-vars.cmake")

        # Magnum contains just the main library
        self.cpp_info.components["magnum_main"].set_property("cmake_target_name", "Magnum::Magnum")
        self.cpp_info.components["magnum_main"].names["cmake_find_package"] = "Magnum"
        self.cpp_info.components["magnum_main"].names["cmake_find_package_multi"] = "Magnum"
        self.cpp_info.components["magnum_main"].libs = [f"Magnum{lib_suffix}"]
        self.cpp_info.components["magnum_main"].requires = ["_magnum", "corrade::utility"]
        _add_cmake_module("magnum_main", "conan-bugfix-global-target.cmake")

        if self.options.audio:
            _add_component("audio", "Audio",
                           ["magnum_main", "corrade::plugin_manager", "openal::openal"])
            if self.options.scene_graph:
                self.cpp_info.components["audio"].requires += ["scene_graph"]
        if self.options.debug_tools:
            _add_component("debug_tools", "DebugTools",
                           ["magnum_main"])
            if self.dependencies["corrade"].options.with_testsuite and self.options.trade:
                self.cpp_info.components["debug_tools"].requires += ["corrade::test_suite", "trade"]
        if self.options.gl:
            _add_component("gl", "GL",
                           ["magnum_main", "opengl::opengl"])
        if self.options.mesh_tools:
            _add_component("mesh_tools", "MeshTools",
                           ["magnum_main", "trade", "gl"])
        if self.options.primitives:
            _add_component("primitives", "Primitives",
                           ["magnum_main", "mesh_tools", "trade"])
        if self.options.scene_graph:
            _add_component("scene_graph", "SceneGraph",
                           ["magnum_main"])
        if self.options.shaders:
            _add_component("shaders", "Shaders",
                           ["magnum_main", "gl"])
        if self.options.text:
            _add_component("text", "Text",
                           ["magnum_main", "texture_tools", "corrade::plugin_manager", "gl"])
        if self.options.texture_tools:
            _add_component("texture_tools", "TextureTools",
                           ["magnum_main", "corrade::plugin_manager", "gl"])
            if self.options.gl:
                self.cpp_info.components["texture_tools"].requires += ["gl"]
        if self.options.trade:
            _add_component("trade", "Trade",
                           ["magnum_main", "corrade::plugin_manager"])
        if self.options.vk:
            _add_component("vk", "Vk",
                           ["magnum_main", "vulkan-loader::vulkan-loader"])

        #### APPLICATIONS ####
        if self.options.get_safe("android_application", False):
            raise Exception("Recipe doesn't define this component")
        if self.options.get_safe("emscripten_application", False):
            raise Exception("Recipe doesn't define this component")
        if self.options.get_safe("windowless_ios_application", False):
            raise Exception("Recipe doesn't define this component")
        if self.options.get_safe("glx_application", False):
            _add_component("glx_application", "GlxApplication",
                           ["gl"]) # TODO: Add x11 requirement
        if self.options.glfw_application:
            _add_component("glfw_application", "GlfwApplication",
                           ["magnum_main", "glfw::glfw"])
            if self.options.target_gl:
                self.cpp_info.components["glfw_application"].requires.append("gl")
        if self.options.sdl2_application:
            _add_component("sdl2_application", "Sdl2Application",
                           ["magnum_main", "sdl::sdl"])
            if self.options.target_gl:
                self.cpp_info.components["sdl2_application"].requires += ["gl"]
        if self.options.get_safe("xegl_application", False):
            _add_component("xegl_application", "XEglApplication",
                           ["gl", "egl::egl"]) # TODO: Add x11 requirement
        if self.options.get_safe("windowless_cgl_application", False):
            _add_component("windowless_cgl_application", "WindowlessCglApplication",
                           ["gl"])
        if self.options.get_safe("windowless_egl_application", False):
            _add_component("windowless_egl_application", "WindowlessEglApplication",
                           ["gl", "egl::egl"])
        if self.options.get_safe("windowless_glx_application", False):
            _add_component("windowless_glx_application", "WindowlessGlxApplication",
                           ["gl"]) # TODO: Add x11 requirement
        if self.options.get_safe("windowless_wgl_application", False):
            _add_component("windowless_wgl_application", "WindowlessWglApplication",
                           ["gl"])
        if self.options.get_safe("windowless_windows_egl_application", False):
            raise Exception("Recipe doesn't define this component")

        # # If there is only one application, here it is an alias
        # self.cpp_info.components["application"].names["cmake_find_package"] = "Application"
        # self.cpp_info.components["application"].names["cmake_find_package_multi"] = "Application"
        # self.cpp_info.components["application"].requires = ["sdl2_application"]

        #### CONTEXTS ####
        if self.options.get_safe("cgl_context", False):
            _add_component("cgl_context", "CglContext",
                           ["gl"])
        if self.options.get_safe("egl_context", False):
            _add_component("egl_context", "EglContext",
                           ["gl", "egl::egl"])
        if self.options.glx_context:
            _add_component("glx_context", "GlxContext",
                           ["gl"])
        if self.options.get_safe("wgl_context", False):
            _add_component("wgl_context", "WglContext",
                           ["gl"])

        ######## PLUGINS ########
        for component, target, library, folder, deps in self._plugins:
            self.cpp_info.components[component].set_property("cmake_target_name", f"Magnum::{target}")
            self.cpp_info.components[component].names["cmake_find_package"] = target
            self.cpp_info.components[component].names["cmake_find_package_multi"] = target
            self.cpp_info.components[component].libs = [f"{library}{plugin_lib_suffix}"]
            self.cpp_info.components[component].libdirs = [os.path.join(self.package_folder, "lib", magnum_plugin_libdir, folder)]
            self.cpp_info.components[component].requires = deps
            if not self.options.shared_plugins:
                _add_cmake_module(component, f"conan-magnum-plugins-{component}.cmake")
        plugin_dir = "bin" if self.settings.os == "Windows" else "lib"
        self.user_info.plugins_basepath = os.path.join(self.package_folder, plugin_dir, magnum_plugin_libdir)
        self.conf_info.define("user.magnum:plugins_basepath", self.user_info.plugins_basepath)

        #### EXECUTABLES ####
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)

        for executable in self._executables:
            _add_cmake_module("_magnum", f"conan-magnum-{executable}.cmake")

        # build modules for CMakeDeps
        self.cpp_info.set_property("cmake_build_modules", build_modules)

    @property
    def _plugins(self):
        # (opt_name, (component, target, library, folder, deps))
        all_plugins = [
            ("any_audio_importer", ("any_audio_importer", "AnyAudioImporter", "AnyAudioImporter", "audioimporters", ["magnum_main", "audio"])),
            ("any_image_converter", ("any_image_converter", "AnyImageConverter", "AnyImageConverter", "imageconverters", ["trade"])),
            ("any_image_importer", ("any_image_importer", "AnyImageImporter", "AnyImageImporter", "importers", ["trade"])),
            ("any_scene_converter", ("any_scene_converter", "AnySceneConverter", "AnySceneConverter", "sceneconverters", ["trade"])),
            ("any_scene_importer", ("any_scene_importer", "AnySceneImporter", "AnySceneImporter", "importers", ["trade"])),
            ("magnum_font", ("magnum_font", "MagnumFont", "MagnumFont", "fonts", ["magnum_main", "trade", "text"])),
            ("magnum_font_converter", ("magnum_font_converter", "MagnumFontConverter", "MagnumFontConverter", "fontconverters", ["magnum_main", "trade", "text", "tga_image_converter"])),
            ("obj_importer", ("obj_importer", "ObjImporter", "ObjImporter", "importers", ["trade", "mesh_tools"])),
            ("tga_importer", ("tga_importer", "TgaImporter", "TgaImporter", "importers", ["trade"])),
            ("tga_image_converter", ("tga_image_converter", "TgaImageConverter", "TgaImageConverter", "imageconverters", ["trade"])),
            ("wav_audio_importer", ("wav_audio_importer", "WavAudioImporter", "WavAudioImporter", "audioimporters", ["magnum_main", "audio"])),
        ]
        return [plugin for opt_name, plugin in all_plugins if self.options.get_safe(opt_name)]
