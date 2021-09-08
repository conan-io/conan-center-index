from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap
import re

required_conan_version = ">=1.33.0"


class MagnumConan(ConanFile):
    name = "magnum"
    description = "Lightweight and modular C++11/C++14 graphics middleware for games and data visualization"
    license = "MIT"
    short_paths = True
    topics = ("magnum", "graphics", "middleware", "graphics", "rendering", "gamedev", "opengl", "3d", "2d", "opengl", "game-engine")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "shared_plugins": [True, False],

        # Follow documented build-options in https://doc.magnum.graphics/magnum/building.html#building-features
        
        "target_gl": [True, False],
        "target_gles": [True, False],
        "target_gles2": [True, False],
        "target_desktop_gles": [True, False],
        "target_headless": [True, False],
        "target_vk": [True, False],

        "with_audio": [True, False],
        "with_debugtools": [True, False],
        "with_gl": [True, False],
        "with_meshtools": [True, False],
        "with_primitives": [True, False],
        "with_scenegraph": [True, False],
        "with_shaders": [True, False],
        #"with_shaderstools": [True, False],  Option not available in sources!
        "with_text": [True, False],
        "with_texturetools": [True, False],
        "with_trade": [True, False],
        "with_vk": [True, False],
        
        "with_androidapplication": [True, False],
        "with_emscriptenapplication": [True, False],
        "with_glfwapplication": [True, False],
        "with_glxapplication": [True, False],
        "with_sdl2application": [True, False],
        "with_xeglapplication": [True, False],
        "with_windowlesscglapplication": [True, False],
        "with_windowlesseglapplication": [True, False],
        "with_windowlessglxapplication": [True, False],
        "with_windowlessiosapplication": [True, False],
        "with_windowlesswglapplication": [True, False],
        "with_windowlesswindowseglapplication": [True, False],

        "with_cglcontext": [True, False],
        "with_eglcontext": [True, False],
        "with_glxcontext": [True, False],
        "with_wglcontext": [True, False],

        "with_gl_info": [True, False],
        # "with_vk_info": [True, False], Not in sources
        "with_al_info": [True, False],
        "with_distancefieldconverter": [True, False],
        "with_fontconverter": [True, False],
        "with_imageconverter": [True, False],
        "with_sceneconverter": [True, False],
        # "with_shaderconverter": [True, False],  Not in sources

        # Options related to plugins
        "with_anyaudioimporter": [True, False],
        "with_anyimageconverter": [True, False],
        "with_anyimageimporter": [True, False],
        "with_anysceneconverter": [True, False],
        "with_anysceneimporter": [True, False],
        #"with_anyshaderconverter": [True, False],  Not in sources
        "with_magnumfont": [True, False],
        "with_magnumfontconverter": [True, False],
        "with_objimporter": [True, False],
        "with_tgaimporter": [True, False],
        "with_tgaimageconverter": [True, False],
        "with_wavaudioimporter": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "shared_plugins": True,

        "target_gl": True,
        "target_gles": True, # TODO: Here we probably have a CHOICE OPTION
        "target_gles2": True, # TODO: Here we probably have a CHOICE OPTION
        "target_desktop_gles": True, # TODO: Here we probably have a CHOICE OPTION
        "target_headless": True,
        "target_vk": True,

        "with_audio": True,
        "with_debugtools": True,
        "with_gl": True,
        "with_meshtools": True,
        "with_primitives": True,
        "with_scenegraph": True,
        "with_shaders": True,
        "with_text": True,
        "with_texturetools": True,
        "with_trade": True,
        "with_vk": True,

        "with_androidapplication": True,
        "with_emscriptenapplication": True,
        "with_glfwapplication": True,
        "with_glxapplication": True,
        "with_sdl2application": True,
        "with_xeglapplication": True,
        "with_windowlesscglapplication": True,
        "with_windowlesseglapplication": True,
        "with_windowlessglxapplication": True,
        "with_windowlessiosapplication": True,
        "with_windowlesswglapplication": True,
        "with_windowlesswindowseglapplication": True,

        "with_cglcontext": True,
        "with_eglcontext": True,
        "with_glxcontext": True,
        "with_wglcontext": True,

        "with_gl_info": True,
        "with_al_info": True,
        "with_distancefieldconverter": True,
        "with_fontconverter": True,
        "with_imageconverter": True,
        "with_sceneconverter": True,

        # Related to plugins
        "with_anyaudioimporter": False,
        "with_anyimageconverter": True,
        "with_anyimageimporter": True,
        "with_anysceneconverter": True,
        "with_anysceneimporter": True,
        "with_magnumfont": True,
        "with_magnumfontconverter": True,
        "with_objimporter": True,
        "with_tgaimporter": True,
        "with_tgaimageconverter": True,
        "with_wavaudioimporter": False,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "cmake/*"]
    
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def config_options(self):
        # Doc says that 'with_distancefieldconverter' is only available with "desktop GL" (the same is said for 'fontconverter', but it builds)
        # TODO: Here we probably have a CHOICE OPTION
        if self.options.target_gles or self.options.target_gles2:
            del self.options.with_distancefieldconverter

        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.target_gles
            del self.options.target_gles2
            del self.options.with_eglcontext
            del self.options.with_xeglapplication
            del self.options.with_windowlesseglapplication
            del self.options.with_windowlessiosapplication
            del self.options.with_windowlessglxapplication
            del self.options.with_windowlesswindowseglapplication  # requires ANGLE
            del self.options.target_headless  # Requires EGL (when used with_gl_info)
            del self.options.with_glxapplication
            del self.options.with_cglcontext
            del self.options.with_windowlesscglapplication

        if self.settings.os == "Linux":
            del self.options.with_cglcontext
            del self.options.with_windowlesscglapplication
            del self.options.with_wglcontext
            del self.options.with_windowlesswglapplication
            del self.options.with_windowlesswindowseglapplication
        
        if self.settings.os == "Macos":
            del self.options.with_eglcontext
            del self.options.target_gles
            del self.options.target_gles2
            del self.options.with_glxapplication  # Requires GL/glx.h (maybe XQuartz project)
            del self.options.with_xeglapplication
            del self.options.with_windowlesseglapplication
            del self.options.with_windowlessglxapplication  # Requires GL/glx.h (maybe XQuartz project)
            del self.options.with_windowlesswglapplication
            del self.options.with_windowlesswindowseglapplication
            del self.options.target_headless  # Requires EGL (when used with_gl_info)

        if self.settings.os != "Android":
            del self.options.with_androidapplication

        if self.settings.os != "Emscripten":
            del self.options.with_emscriptenapplication

        if self.settings.os != "iOS":
            del self.options.with_windowlessiosapplication

    @property
    def _executables(self):
        all_execs = ("gl-info", "al-info", "distancefieldconverter", "fontconverter", "imageconverter", "sceneconverter")
        return [it for it in all_execs if self.options.get_safe("with_{}".format(it.replace("-", "_")))]

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
    
    def requirements(self):
        self.requires("corrade/{}".format(self.version))
        if self.options.with_audio:
            self.requires("openal/1.21.1")
        if self.options.with_gl:
            self.requires("opengl/system")
        if self.options.with_vk:
            self.requires("vulkan-loader/1.2.190")

        if self.options.get_safe("with_eglcontext", False) or \
           self.options.get_safe("with_xeglapplication", False) or \
           self.options.get_safe("with_windowlesseglapplication", False) or \
           self.options.get_safe("with_windowlessiosapplication") or \
           self.options.get_safe("with_windowlesswindowseglapplication", False) or \
           self.options.get_safe("target_headless", False):
            self.requires("egl/system")

        if self.options.with_glfwapplication:
            self.requires("glfw/3.3.4")

        if self.options.with_sdl2application:
            self.requires("sdl/2.0.16")

    def build_requirements(self):
        self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5.0":
            raise ConanInvalidConfiguration("GCC older than 5 is not supported (missing C++11 features)")

        if self.options.shared and not self.options["corrade"].shared:
            # To fix issue with resource management, see here: https://github.com/mosra/magnum/issues/304#issuecomment-451768389
            raise ConanInvalidConfiguration("If using 'shared=True', corrade should be shared as well")

        if not self.options.with_gl and (self.options.target_gl or 
                                         self.options.get_safe("target_gles", False) or
                                         self.options.get_safe("target_gles2", False) or
                                         self.options.target_desktop_gles or
                                         self.options.get_safe("target_headless", False)):
            raise ConanInvalidConfiguration("Option 'with_gl=True' is required")
        if not self.options.with_vk and self.options.target_vk:
            raise ConanInvalidConfiguration("Option 'with_vk=True' is required")

        if self.options.get_safe("with_cglcontext", False) and not self.options.target_gl:
            raise ConanInvalidConfiguration("Option 'with_cglcontext' requires 'target_gl=True'")

        if self.options.get_safe("target_gles2", False) and not self.options.get_safe("target_gles", False):
            raise ConanInvalidConfiguration("Option 'target_gles2' requires 'target_gles=True'")

        if self.options.get_safe("with_windowlesscglapplication", False) and not self.options.target_gl:
            raise ConanInvalidConfiguration("Option 'with_windowlesscglapplication' requires 'target_gl=True'")

        if self.options.with_al_info and not self.options.with_audio:
            raise ConanInvalidConfiguration("Option 'with_al_info' requires 'with_audio=True'")

        if self.options.with_magnumfontconverter and not self.options.with_tgaimageconverter:
            raise ConanInvalidConfiguration("magnumfontconverter requires tgaimageconverter")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_DEPRECATED"] = False
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        # self._cmake.definitions["BUILD_STATIC_UNIQUE_GLOBALS"]
        self._cmake.definitions["BUILD_PLUGINS_STATIC"] = not self.options.shared_plugins
        self._cmake.definitions["LIB_SUFFIX"] = ""
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_GL_TESTS"] = False
        self._cmake.definitions["BUILD_AL_TESTS"] = False
        self._cmake.definitions["WITH_OPENGLTESTER"] = False
        self._cmake.definitions["WITH_VULKANTESTER"] = False

        self._cmake.definitions["TARGET_GL"] = self.options.target_gl
        self._cmake.definitions["TARGET_GLES"] = self.options.get_safe("target_gles", False)
        self._cmake.definitions["TARGET_GLES2"] = self.options.get_safe("target_gles2", False)
        self._cmake.definitions["TARGET_DESKTOP_GLES"] = self.options.target_desktop_gles
        self._cmake.definitions["TARGET_HEADLESS"] = self.options.get_safe("target_headless", False)
        self._cmake.definitions["TARGET_VK"] = self.options.target_vk

        self._cmake.definitions["WITH_AUDIO"] = self.options.with_audio
        self._cmake.definitions["WITH_DEBUGTOOLS"] = self.options.with_debugtools
        self._cmake.definitions["WITH_GL"] = self.options.with_gl
        self._cmake.definitions["WITH_MESHTOOLS"] = self.options.with_meshtools
        self._cmake.definitions["WITH_PRIMITIVES"] = self.options.with_primitives
        self._cmake.definitions["WITH_SCENEGRAPH"] = self.options.with_scenegraph
        self._cmake.definitions["WITH_SHADERS"] = self.options.with_shaders
        self._cmake.definitions["WITH_TEXT"] = self.options.with_text
        self._cmake.definitions["WITH_TEXTURETOOLS"] = self.options.with_texturetools
        self._cmake.definitions["WITH_TRADE"] = self.options.with_trade
        self._cmake.definitions["WITH_VK"] = self.options.with_vk

        self._cmake.definitions["WITH_ANDROIDAPPLICATION"] = self.options.get_safe("with_androidapplication", False)
        self._cmake.definitions["WITH_EMSCRIPTENAPPLICATION"] = self.options.get_safe("with_emscriptenapplication", False)
        self._cmake.definitions["WITH_GLFWAPPLICATION"] = self.options.with_glfwapplication
        self._cmake.definitions["WITH_GLXAPPLICATION"] = self.options.get_safe("with_glxapplication", False)
        self._cmake.definitions["WITH_SDL2APPLICATION"] = self.options.with_sdl2application
        self._cmake.definitions["WITH_XEGLAPPLICATION"] = self.options.get_safe("with_xeglapplication", False)
        self._cmake.definitions["WITH_WINDOWLESSCGLAPPLICATION"] = self.options.get_safe("with_windowlesscglapplication", False)
        self._cmake.definitions["WITH_WINDOWLESSEGLAPPLICATION"] = self.options.get_safe("with_windowlesseglapplication", False)
        self._cmake.definitions["WITH_WINDOWLESSGLXAPPLICATION"] = self.options.get_safe("with_windowlessglxapplication", False)
        self._cmake.definitions["WITH_WINDOWLESSIOSAPPLICATION"] = self.options.get_safe("with_windowlessiosapplication", False)
        self._cmake.definitions["WITH_WINDOWLESSWGLAPPLICATION"] = self.options.get_safe("with_windowlesswglapplication", False)
        self._cmake.definitions["WITH_WINDOWLESSWINDOWSEGLAPPLICATION"] = self.options.get_safe("with_windowlesswindowseglapplication", False)

        self._cmake.definitions["WITH_CGLCONTEXT"] = self.options.get_safe("with_cglcontext", False)
        self._cmake.definitions["WITH_EGLCONTEXT"] = self.options.get_safe("with_eglcontext", False)
        self._cmake.definitions["WITH_GLXCONTEXT"] = self.options.with_glxcontext
        self._cmake.definitions["WITH_WGLCONTEXT"] = self.options.get_safe("with_wglcontext", False)

        ##### Plugins related #####
        self._cmake.definitions["WITH_ANYAUDIOIMPORTER"] = self.options.with_anyaudioimporter
        self._cmake.definitions["WITH_ANYIMAGECONVERTER"] = self.options.with_anyimageconverter
        self._cmake.definitions["WITH_ANYIMAGEIMPORTER"] = self.options.with_anyimageimporter
        self._cmake.definitions["WITH_ANYSCENECONVERTER"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_ANYSCENEIMPORTER"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_MAGNUMFONT"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_MAGNUMFONTCONVERTER"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_OBJIMPORTER"] = self.options.with_objimporter
        self._cmake.definitions["WITH_TGAIMPORTER"] = self.options.with_tgaimporter
        self._cmake.definitions["WITH_TGAIMAGECONVERTER"] = self.options.with_tgaimageconverter
        self._cmake.definitions["WITH_WAVAUDIOIMPORTER"] = self.options.with_wavaudioimporter

        #### Command line utilities ####
        self._cmake.definitions["WITH_GL_INFO"] = self.options.with_gl_info
        self._cmake.definitions["WITH_AL_INFO"] = self.options.with_al_info
        self._cmake.definitions["WITH_DISTANCEFIELDCONVERTER"] = self.options.get_safe("with_distancefieldconverter", False)
        self._cmake.definitions["WITH_FONTCONVERTER"] = self.options.with_fontconverter
        self._cmake.definitions["WITH_IMAGECONVERTER"] = self.options.with_imageconverter
        self._cmake.definitions["WITH_SCENECONVERTER"] = self.options.with_sceneconverter

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})',
                              "")
        # Get rid of cmake_dependent_option, it can activate features when we try to disable them,
        #   let the Conan user decide what to use and what not.
        with open(os.path.join(self._source_subfolder, "CMakeLists.txt"), 'r+') as f:
            text = f.read()
            text = re.sub('cmake_dependent_option\(([0-9A-Z_]+) .*\)', r'option(\1 "Option \1 disabled by Conan" OFF)', text)
            f.seek(0)
            f.write(text)
            f.truncate()

        # GLFW naming
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "find_package(GLFW)",
                              "find_package(glfw3)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "GLFW_FOUND",
                              "glfw3_FOUND")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "GLFW::GLFW",
                              "glfw::glfw")

        # EGL naming
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "find_package(EGL)",
                              "find_package(egl_system)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "EGL_FOUND",
                              "egl_system_FOUND")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "EGL::EGL",
                              "egl::egl")

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        build_modules_folder = os.path.join(self.package_folder, "lib", "cmake")
        os.makedirs(build_modules_folder)
        for exec in self._executables:
            build_module_path = os.path.join(build_modules_folder, "conan-magnum-{}.cmake".format(exec))
            with open(build_module_path, "w+") as f:
                f.write(textwrap.dedent("""\
                    if(NOT TARGET Magnum::{exec})
                        if(CMAKE_CROSSCOMPILING)
                            find_program(MAGNUM_EXEC_PROGRAM magnum-{exec} PATHS ENV PATH NO_DEFAULT_PATH)
                        endif()
                        if(NOT MAGNUM_EXEC_PROGRAM)
                            set(MAGNUM_EXEC_PROGRAM "${{CMAKE_CURRENT_LIST_DIR}}/../../bin/magnum-{exec}")
                        endif()
                        get_filename_component(MAGNUM_EXEC_PROGRAM "${{MAGNUM_EXEC_PROGRAM}}" ABSOLUTE)
                        add_executable(Magnum::{exec} IMPORTED)
                        set_property(TARGET Magnum::{exec} PROPERTY IMPORTED_LOCATION ${{MAGNUM_EXEC_PROGRAM}})
                    endif()
                """.format(exec=exec)))

        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("*.cmake", src=os.path.join(self.source_folder, "cmake"), dst=os.path.join("lib", "cmake"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Magnum"
        self.cpp_info.names["cmake_find_package_multi"] = "Magnum"

        magnum_plugin_libdir = "magnum-d" if self.settings.build_type == "Debug" else "magnum"
        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""

        # The FindMagnum.cmake file provided by the library populates some extra stuff
        self.cpp_info.components["_magnum"].build_modules.append(os.path.join("lib", "cmake", "conan-magnum-vars.cmake"))

        # Magnum contains just the main library
        self.cpp_info.components["magnum_main"].names["cmake_find_package"] = "Magnum"
        self.cpp_info.components["magnum_main"].names["cmake_find_package_multi"] = "Magnum"
        self.cpp_info.components["magnum_main"].libs = ["Magnum{}".format(lib_suffix)]
        self.cpp_info.components["magnum_main"].requires = ["_magnum", "corrade::utility"]

        # Audio
        if self.options.with_audio:
            self.cpp_info.components["audio"].names["cmake_find_package"] = "Audio"
            self.cpp_info.components["audio"].names["cmake_find_package_multi"] = "Audio"
            self.cpp_info.components["audio"].libs = ["MagnumAudio{}".format(lib_suffix)]
            self.cpp_info.components["audio"].requires = ["magnum_main", "corrade::plugin_manager", "openal::openal"]
            if self.options.with_scenegraph:
                self.cpp_info.components["audio"].requires += ["scenegraph"] 

        # DebugTools
        if self.options.with_debugtools:
            self.cpp_info.components["debugtools"].names["cmake_find_package"] = "DebugTools"
            self.cpp_info.components["debugtools"].names["cmake_find_package_multi"] = "DebugTools"
            self.cpp_info.components["debugtools"].libs = ["MagnumDebugTools{}".format(lib_suffix)]
            self.cpp_info.components["debugtools"].requires = ["magnum_main"]
            if self.options["corrade"].with_testsuite and self.options.with_trade:
                self.cpp_info.components["debugtools"].requires += ["corrade::test_suite", "trade"]

        # GL
        if self.options.with_gl:
            self.cpp_info.components["gl"].names["cmake_find_package"] = "GL"
            self.cpp_info.components["gl"].names["cmake_find_package_multi"] = "GL"
            self.cpp_info.components["gl"].libs = ["MagnumGL{}".format(lib_suffix)]
            self.cpp_info.components["gl"].requires = ["magnum_main", "opengl::opengl"]

        # MeshTools
        if self.options.with_meshtools:
            self.cpp_info.components["meshtools"].names["cmake_find_package"] = "MeshTools"
            self.cpp_info.components["meshtools"].names["cmake_find_package_multi"] = "MeshTools"
            self.cpp_info.components["meshtools"].libs = ["MagnumMeshTools{}".format(lib_suffix)]
            self.cpp_info.components["meshtools"].requires = ["magnum_main", "trade", "gl"]

        # Primitives
        if self.options.with_primitives:
            self.cpp_info.components["primitives"].names["cmake_find_package"] = "Primitives"
            self.cpp_info.components["primitives"].names["cmake_find_package_multi"] = "Primitives"
            self.cpp_info.components["primitives"].libs = ["MagnumPrimitives{}".format(lib_suffix)]
            self.cpp_info.components["primitives"].requires = ["magnum_main", "meshtools", "trade"]

        # SceneGraph
        if self.options.with_scenegraph:
            self.cpp_info.components["scenegraph"].names["cmake_find_package"] = "SceneGraph"
            self.cpp_info.components["scenegraph"].names["cmake_find_package_multi"] = "SceneGraph"
            self.cpp_info.components["scenegraph"].libs = ["MagnumSceneGraph{}".format(lib_suffix)]
            self.cpp_info.components["scenegraph"].requires = ["magnum_main"]

        # Shaders
        if self.options.with_scenegraph:
            self.cpp_info.components["shaders"].names["cmake_find_package"] = "Shaders"
            self.cpp_info.components["shaders"].names["cmake_find_package_multi"] = "Shaders"
            self.cpp_info.components["shaders"].libs = ["MagnumShaders{}".format(lib_suffix)]
            self.cpp_info.components["shaders"].requires = ["magnum_main", "gl"]

        # Text
        if self.options.with_text:
            self.cpp_info.components["text"].names["cmake_find_package"] = "Text"
            self.cpp_info.components["text"].names["cmake_find_package_multi"] = "Text"
            self.cpp_info.components["text"].libs = ["MagnumText{}".format(lib_suffix)]
            self.cpp_info.components["text"].requires = ["magnum_main", "texturetools", "corrade::plugin_manager", "gl"]

        # TextureTools
        if self.options.with_texturetools:
            self.cpp_info.components["texturetools"].names["cmake_find_package"] = "TextureTools"
            self.cpp_info.components["texturetools"].names["cmake_find_package_multi"] = "TextureTools"
            self.cpp_info.components["texturetools"].libs = ["MagnumTextureTools{}".format(lib_suffix)]
            self.cpp_info.components["texturetools"].requires = ["magnum_main"]
            if self.options.with_gl:
                self.cpp_info.components["texturetools"].requires += ["gl"]

        # Trade
        if self.options.with_trade:
            self.cpp_info.components["trade"].names["cmake_find_package"] = "Trade"
            self.cpp_info.components["trade"].names["cmake_find_package_multi"] = "Trade"
            self.cpp_info.components["trade"].libs = ["MagnumTrade{}".format(lib_suffix)]
            self.cpp_info.components["trade"].requires = ["magnum_main", "corrade::plugin_manager"]

        # VK
        if self.options.with_vk:
            self.cpp_info.components["vk"].names["cmake_find_package"] = "Vk"
            self.cpp_info.components["vk"].names["cmake_find_package_multi"] = "Vk"
            self.cpp_info.components["vk"].libs = ["MagnumVk{}".format(lib_suffix)]
            self.cpp_info.components["vk"].requires = ["magnum_main", "vulkan-loader::vulkan-loader"]


        #### APPLICATIONS ####
        if self.options.get_safe("with_androidapplication", False):
            raise Exception("Recipe doesn't define this component")

        if self.options.get_safe("with_emscriptenapplication", False):
            raise Exception("Recipe doesn't define this component")

        if self.options.get_safe("with_windowlessiosapplication", False):
            raise Exception("Recipe doesn't define this component")

        if self.options.get_safe("with_glxapplication", False):
            self.cpp_info.components["glx_application"].names["cmake_find_package"] = "GlxApplication"
            self.cpp_info.components["glx_application"].names["cmake_find_package_multi"] = "GlxApplication"
            self.cpp_info.components["glx_application"].libs = ["MagnumGlxApplication{}".format(lib_suffix)]
            self.cpp_info.components["glx_application"].requires = ["gl"]  # TODO: Add x11

        if self.options.with_glfwapplication:
            self.cpp_info.components["glfw_application"].names["cmake_find_package"] = "GlfwApplication"
            self.cpp_info.components["glfw_application"].names["cmake_find_package_multi"] = "GlfwApplication"
            self.cpp_info.components["glfw_application"].libs = ["MagnumGlfwApplication{}".format(lib_suffix)]
            self.cpp_info.components["glfw_application"].requires = ["magnum_main", "glfw::glfw"]
            if self.options.target_gl:
                self.cpp_info.components["glfw_application"].requires.append("gl")

        if self.options.with_sdl2application:
            self.cpp_info.components["sdl2_application"].names["cmake_find_package"] = "Sdl2Application"
            self.cpp_info.components["sdl2_application"].names["cmake_find_package_multi"] = "Sdl2Application"
            self.cpp_info.components["sdl2_application"].libs = ["MagnumSdl2Application{}".format(lib_suffix)]
            self.cpp_info.components["sdl2_application"].requires = ["magnum_main", "sdl::sdl"]
            if self.options.target_gl:
                self.cpp_info.components["sdl2_application"].requires += ["gl"]

        if self.options.get_safe("with_xeglapplication", False):
            self.cpp_info.components["xegl_application"].names["cmake_find_package"] = "XEglApplication"
            self.cpp_info.components["xegl_application"].names["cmake_find_package_multi"] = "XEglApplication"
            self.cpp_info.components["xegl_application"].libs = ["MagnumXEglApplication{}".format(lib_suffix)]
            self.cpp_info.components["xegl_application"].requires = ["gl", "egl::egl"] # TODO: Add x11

        if self.options.get_safe("with_windowlesscglapplication", False):
            self.cpp_info.components["windowless_cgl_application"].names["cmake_find_package"] = "WindowlessCglApplication"
            self.cpp_info.components["windowless_cgl_application"].names["cmake_find_package_multi"] = "WindowlessCglApplication"
            self.cpp_info.components["windowless_cgl_application"].libs = ["MagnumWindowlessCglApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_cgl_application"].requires = ["gl"]

        if self.options.get_safe("with_windowlesseglapplication", False):
            self.cpp_info.components["windowless_egl_application"].names["cmake_find_package"] = "WindowlessEglApplication"
            self.cpp_info.components["windowless_egl_application"].names["cmake_find_package_multi"] = "WindowlessEglApplication"
            self.cpp_info.components["windowless_egl_application"].libs = ["MagnumWindowlessEglApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_egl_application"].requires = ["gl", "egl::egl"]

        if self.options.get_safe("with_windowlessglxapplication", False):
            self.cpp_info.components["windowless_glx_application"].names["cmake_find_package"] = "WindowlessGlxApplication"
            self.cpp_info.components["windowless_glx_application"].names["cmake_find_package_multi"] = "WindowlessGlxApplication"
            self.cpp_info.components["windowless_glx_application"].libs = ["MagnumWindowlessGlxApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_glx_application"].requires = ["gl"]  # TODO: Add x11

        if self.options.get_safe("with_windowlesswglapplication", False):
            self.cpp_info.components["windowlesswglapplication"].names["cmake_find_package"] = "WindowlessWglApplication"
            self.cpp_info.components["windowlesswglapplication"].names["cmake_find_package_multi"] = "WindowlessWglApplication"
            self.cpp_info.components["windowlesswglapplication"].libs = ["MagnumWindowlessWglApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_glx_application"].requires = ["gl"]

        if self.options.get_safe("with_windowlesswindowseglapplication", False):
            raise Exception("Recipe doesn't define this component")

        """
            # If there is only one application, here it is an alias
            self.cpp_info.components["application"].names["cmake_find_package"] = "Application"
            self.cpp_info.components["application"].names["cmake_find_package_multi"] = "Application"
            self.cpp_info.components["application"].requires = ["sdl2_application"]
        """

        #### CONTEXTS ####
        if self.options.get_safe("with_cglcontext", False):
            self.cpp_info.components["cglcontext"].names["cmake_find_package"] = "CglContext"
            self.cpp_info.components["cglcontext"].names["cmake_find_package_multi"] = "CglContext"
            self.cpp_info.components["cglcontext"].libs = ["MagnumCglContext{}".format(lib_suffix)]
            self.cpp_info.components["cglcontext"].requires = ["gl"]

        if self.options.get_safe("with_eglcontext", False):
            self.cpp_info.components["eglcontext"].names["cmake_find_package"] = "EglContext"
            self.cpp_info.components["eglcontext"].names["cmake_find_package_multi"] = "EglContext"
            self.cpp_info.components["eglcontext"].libs = ["MagnumEglContext{}".format(lib_suffix)]
            self.cpp_info.components["eglcontext"].requires = ["gl", "egl::egl"]

        if self.options.with_glxcontext:
            self.cpp_info.components["glxcontext"].names["cmake_find_package"] = "GlxContext"
            self.cpp_info.components["glxcontext"].names["cmake_find_package_multi"] = "GlxContext"
            self.cpp_info.components["glxcontext"].libs = ["MagnumGlxContext{}".format(lib_suffix)]
            self.cpp_info.components["glxcontext"].requires = ["gl"]

        if self.options.get_safe("with_wglcontext", False):
            self.cpp_info.components["wglcontext"].names["cmake_find_package"] = "WglContext"
            self.cpp_info.components["wglcontext"].names["cmake_find_package_multi"] = "WglContext"
            self.cpp_info.components["wglcontext"].libs = ["MagnumWglContext{}".format(lib_suffix)]
            self.cpp_info.components["wglcontext"].requires = ["gl"]


        ######## PLUGINS ########
        # If shared, there are no libraries to link with
        if self.options.with_anyaudioimporter:
            raise Exception("Create component here")

        if self.options.with_anyimageconverter:
            self.cpp_info.components["anyimageconverter"].names["cmake_find_package"] = "AnyImageConverter"
            self.cpp_info.components["anyimageconverter"].names["cmake_find_package_multi"] = "AnyImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anyimageconverter"].libs = ["AnyImageConverter"]
                self.cpp_info.components["anyimageconverter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'imageconverters')]
            self.cpp_info.components["anyimageconverter"].requires = ["trade"]

        if self.options.with_anyimageimporter:
            self.cpp_info.components["anyimageimporter"].names["cmake_find_package"] = "AnyImageImporter"
            self.cpp_info.components["anyimageimporter"].names["cmake_find_package_multi"] = "AnyImageImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anyimageimporter"].libs = ["AnyImageImporter"]
                self.cpp_info.components["anyimageimporter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["anyimageimporter"].requires = ["trade"]

        if self.options.with_anysceneconverter:
            self.cpp_info.components["anysceneconverter"].names["cmake_find_package"] = "AnySceneConverter"
            self.cpp_info.components["anysceneconverter"].names["cmake_find_package_multi"] = "AnySceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anysceneconverter"].libs = ["AnySceneConverter"]
                self.cpp_info.components["anysceneconverter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'sceneconverters')]
            self.cpp_info.components["anysceneconverter"].requires = ["trade"]

        if self.options.with_anysceneimporter:
            self.cpp_info.components["anysceneimporter"].names["cmake_find_package"] = "AnySceneImporter"
            self.cpp_info.components["anysceneimporter"].names["cmake_find_package_multi"] = "AnySceneImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anysceneimporter"].libs = ["AnySceneImporter"]
                self.cpp_info.components["anysceneimporter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["anysceneimporter"].requires = ["trade"]

        if self.options.with_magnumfont:
            self.cpp_info.components["magnumfont"].names["cmake_find_package"] = "MagnumFont"
            self.cpp_info.components["magnumfont"].names["cmake_find_package_multi"] = "MagnumFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["magnumfont"].libs = ["MagnumFont"]
                self.cpp_info.components["magnumfont"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'fonts')]
            self.cpp_info.components["magnumfont"].requires = ["magnum_main", "trade", "text"]

        if self.options.with_magnumfontconverter:
            self.cpp_info.components["magnumfontconverter"].names["cmake_find_package"] = "MagnumFontConverter"
            self.cpp_info.components["magnumfontconverter"].names["cmake_find_package_multi"] = "MagnumFontConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["magnumfontconverter"].libs = ["MagnumFontConverter"]
                self.cpp_info.components["magnumfontconverter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'fontconverters')]
            self.cpp_info.components["magnumfontconverter"].requires = ["magnum_main", "trade", "text"]
            if not self.options.shared_plugins:
                self.cpp_info.components["magnumfontconverter"].requires += ["tgaimageconverter"]

        if self.options.with_objimporter:
            self.cpp_info.components["objimporter"].names["cmake_find_package"] = "ObjImporter"
            self.cpp_info.components["objimporter"].names["cmake_find_package_multi"] = "ObjImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["objimporter"].libs = ["ObjImporter"]
                self.cpp_info.components["objimporter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["objimporter"].requires = ["trade", "meshtools"]

        if self.options.with_tgaimporter:
            self.cpp_info.components["tgaimporter"].names["cmake_find_package"] = "TgaImporter"
            self.cpp_info.components["tgaimporter"].names["cmake_find_package_multi"] = "TgaImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["tgaimporter"].libs = ["TgaImporter"]
                self.cpp_info.components["tgaimporter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["tgaimporter"].requires = ["trade"]

        if self.options.with_tgaimageconverter:
            self.cpp_info.components["tgaimageconverter"].names["cmake_find_package"] = "TgaImageConverter"
            self.cpp_info.components["tgaimageconverter"].names["cmake_find_package_multi"] = "TgaImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["tgaimageconverter"].libs = ["TgaImageConverter"]
                self.cpp_info.components["tgaimageconverter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'imageconverters')]
            self.cpp_info.components["tgaimageconverter"].requires = ["trade"]

        if self.options.with_wavaudioimporter:
            raise Exception("Component required here")

        #### EXECUTABLES ####
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        for exec in self._executables:
            self.cpp_info.components["_magnum"].build_modules.append(os.path.join("lib", "cmake", "conan-magnum-{}.cmake".format(exec)))
