from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class MagnumConan(ConanFile):
    name = "magnum"
    description = "Lightweight and modular C++11/C++14 graphics middleware for games and data visualization"
    license = "MIT"
    topics = ("conan", "corrade", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sdl2_application": [True, False],

        "with_audio": [True, False],
        "with_debugtools": [True, False],
        "with_meshtools": [True, False],
        "with_gl": [True, False],
        "with_primitives": [True, False],
        "with_scenegraph": [True, False],
        "with_shaders": [True, False],
        "with_text": [True, False],
        "with_texturetools": [True, False],
        "with_trade": [True, False],
        "with_vk": [True, False],

        "with_cglcontext": [True, False],

        # Options related to plugins
        "shared_plugins": [True, False],
        # WITH_ANYAUDIOIMPORTER
        "with_anyimageimporter": [True, False],
        "with_anyimageconverter": [True, False],
        "with_anysceneconverter": [True, False],
        "with_anysceneimporter": [True, False],
        "with_magnumfont": [True, False],
        "with_magnumfontconverter": [True, False],
        "with_objimporter": [True, False],
        "with_tgaimageconverter": [True, False],
        "with_tgaimporter": [True, False],
        #"with_wavaudioimporter": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "sdl2_application": True,

        "with_audio": False,
        "with_debugtools": True,
        "with_meshtools": True,
        "with_gl": True,
        "with_primitives": True,
        "with_scenegraph": True,
        "with_shaders": True,
        "with_text": True,
        "with_texturetools": True,
        "with_trade": True,
        "with_vk": True,

        "with_cglcontext": True,

        "shared_plugins": True,
        "with_anyimageimporter": True,
        "with_anyimageconverter": True,
        "with_anysceneconverter": True,
        "with_anysceneimporter": True,
        "with_magnumfont": True,
        "with_magnumfontconverter": True,
        "with_objimporter": True,
        "with_tgaimageconverter": True,
        "with_tgaimporter": True,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "cmake/*"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})',
                              "")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Macos":
            del self.options.with_cglcontext

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
    
    def requirements(self):
        self.requires("corrade/{}".format(self.version))
        if self.options.with_gl:
            self.requires("opengl/system")
        if self.options.sdl2_application:
            self.requires("sdl/2.0.16")
        if self.options.with_vk:
            self.requires("vulkan-loader/1.2.182")

    def build_requirements(self):
        self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if self.options.shared and not self.options["corrade"].shared:
            # To fix issue with resource management, see here: https://github.com/mosra/magnum/issues/304#issuecomment-451768389
            raise ConanInvalidConfiguration("If using 'shared=True', corrade should be shared as well")

        if self.options.with_magnumfontconverter and not self.options.with_tgaimageconverter:
            raise ConanInvalidConfiguration("magnumfontconverter requires tgaimageconverter")

        if self.options.get_safe("with_cglcontext", False) and not self.options.with_gl:
            raise ConanInvalidConfiguration("Option 'with_cglcontext' requires option 'with_gl'")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        self._cmake.definitions["LIB_SUFFIX"] = ""
        self._cmake.definitions["BUILD_TESTS"] = False

        self._cmake.definitions["WITH_SDL2APPLICATION"] = self.options.sdl2_application

        self._cmake.definitions["WITH_AUDIO"] = self.options.with_audio
        self._cmake.definitions["WITH_DEBUGTOOLS"] = self.options.with_debugtools
        self._cmake.definitions["WITH_MESHTOOLS"] = self.options.with_meshtools
        self._cmake.definitions["WITH_GL"] = self.options.with_gl
        self._cmake.definitions["WITH_PRIMITIVES"] = self.options.with_primitives
        self._cmake.definitions["WITH_SCENEGRAPH"] = self.options.with_scenegraph
        self._cmake.definitions["WITH_SHADERS"] = self.options.with_shaders
        self._cmake.definitions["WITH_TEXT"] = self.options.with_text
        self._cmake.definitions["WITH_TEXTURETOOLS"] = self.options.with_texturetools
        self._cmake.definitions["WITH_TRADE"] = self.options.with_trade
        self._cmake.definitions["WITH_VK"] = self.options.with_vk

        self._cmake.definitions["WITH_CGLCONTEXT"] = self.options.get_safe("with_cglcontext", False)

        ##### Plugins related #####
        self._cmake.definitions["BUILD_PLUGINS_STATIC"] = not self.options.shared_plugins
        self._cmake.definitions["WITH_ANYIMAGEIMPORTER"] = self.options.with_anyimageimporter
        self._cmake.definitions["WITH_ANYIMAGECONVERTER"] = self.options.with_anyimageconverter
        self._cmake.definitions["WITH_ANYSCENECONVERTER"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_ANYSCENEIMPORTER"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_MAGNUMFONT"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_MAGNUMFONTCONVERTER"] = self.options.with_anysceneconverter
        self._cmake.definitions["WITH_OBJIMPORTER"] = self.options.with_objimporter
        self._cmake.definitions["WITH_TGAIMAGECONVERTER"] = self.options.with_tgaimageconverter
        self._cmake.definitions["WITH_TGAIMPORTER"] = self.options.with_tgaimporter
        
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("*.cmake", src=os.path.join(self.source_folder, "cmake"), dst=os.path.join("lib", "cmake"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Magnum"
        self.cpp_info.names["cmake_find_package_multi"] = "Magnum"

        # The FindMagnum.cmake file provided by the library populates some extra stuff
        self.cpp_info.components["_magnum"].build_modules.append(os.path.join("lib", "cmake", "conan-magnum-vars.cmake"))

        # Magnum contains just the main library
        self.cpp_info.components["magnum_main"].names["cmake_find_package"] = "Magnum"
        self.cpp_info.components["magnum_main"].names["cmake_find_package_multi"] = "Magnum"
        self.cpp_info.components["magnum_main"].libs = ["Magnum"]
        self.cpp_info.components["magnum_main"].requires = ["_magnum", "corrade::utility"]

        # Animation
        # Math 
        # Platform
        if self.options.sdl2_application:
            self.cpp_info.components["sdl2_application"].names["cmake_find_package"] = "Sdl2Application"
            self.cpp_info.components["sdl2_application"].names["cmake_find_package_multi"] = "Sdl2Application"
            self.cpp_info.components["sdl2_application"].libs = ["MagnumSdl2Application"]
            self.cpp_info.components["sdl2_application"].requires = ["magnum_main", "sdl::sdl"]
            if self.options.with_gl:
                self.cpp_info.components["sdl2_application"].requires += ["gl"]

            # If there is only one application, here it is an alias
            self.cpp_info.components["application"].names["cmake_find_package"] = "Application"
            self.cpp_info.components["application"].names["cmake_find_package_multi"] = "Application"
            self.cpp_info.components["application"].requires = ["sdl2_application"]


        # Audio
        # TODO: Here there is a target (false by default)
        
        # DebugTools
        if self.options.with_debugtools:
            self.cpp_info.components["debugtools"].names["cmake_find_package"] = "DebugTools"
            self.cpp_info.components["debugtools"].names["cmake_find_package_multi"] = "DebugTools"
            self.cpp_info.components["debugtools"].libs = ["MagnumDebugTools"]
            self.cpp_info.components["debugtools"].requires = ["magnum_main"]
            if self.options["corrade"].with_testsuite and self.options.with_trade:
                self.cpp_info.components["debugtools"].requires += ["corrade::test_suite", "trade"]

        # GL
        if self.options.with_gl:
            self.cpp_info.components["gl"].names["cmake_find_package"] = "GL"
            self.cpp_info.components["gl"].names["cmake_find_package_multi"] = "GL"
            self.cpp_info.components["gl"].libs = ["MagnumGL"]
            self.cpp_info.components["gl"].requires = ["magnum_main", "opengl::opengl"]

        # MeshTools
        if self.options.with_meshtools:
            self.cpp_info.components["meshtools"].names["cmake_find_package"] = "MeshTools"
            self.cpp_info.components["meshtools"].names["cmake_find_package_multi"] = "MeshTools"
            self.cpp_info.components["meshtools"].libs = ["MagnumMeshTools"]
            self.cpp_info.components["meshtools"].requires = ["magnum_main", "trade", "gl"]

        # Primitives
        if self.options.with_primitives:
            self.cpp_info.components["primitives"].names["cmake_find_package"] = "Primitives"
            self.cpp_info.components["primitives"].names["cmake_find_package_multi"] = "Primitives"
            self.cpp_info.components["primitives"].libs = ["MagnumPrimitives"]
            self.cpp_info.components["primitives"].requires = ["magnum_main", "meshtools", "trade"]

        # SceneGraph
        if self.options.with_scenegraph:
            self.cpp_info.components["scenegraph"].names["cmake_find_package"] = "SceneGraph"
            self.cpp_info.components["scenegraph"].names["cmake_find_package_multi"] = "SceneGraph"
            self.cpp_info.components["scenegraph"].libs = ["MagnumSceneGraph"]
            self.cpp_info.components["scenegraph"].requires = ["magnum_main"]

        # Shaders
        if self.options.with_scenegraph:
            self.cpp_info.components["shaders"].names["cmake_find_package"] = "Shaders"
            self.cpp_info.components["shaders"].names["cmake_find_package_multi"] = "Shaders"
            self.cpp_info.components["shaders"].libs = ["MagnumShaders"]
            self.cpp_info.components["shaders"].requires = ["magnum_main", "gl"]

        # Text
        if self.options.with_text:
            self.cpp_info.components["text"].names["cmake_find_package"] = "Text"
            self.cpp_info.components["text"].names["cmake_find_package_multi"] = "Text"
            self.cpp_info.components["text"].libs = ["MagnumText"]
            self.cpp_info.components["text"].requires = ["magnum_main", "texturetools", "corrade::plugin_manager", "gl"]

        # TextureTools
        if self.options.with_texturetools:
            self.cpp_info.components["texturetools"].names["cmake_find_package"] = "TextureTools"
            self.cpp_info.components["texturetools"].names["cmake_find_package_multi"] = "TextureTools"
            self.cpp_info.components["texturetools"].libs = ["MagnumTextureTools"]
            self.cpp_info.components["texturetools"].requires = ["magnum_main"]
            if self.options.with_gl:
                self.cpp_info.components["texturetools"].requires += ["gl"]

        # Trade
        if self.options.with_trade:
            self.cpp_info.components["trade"].names["cmake_find_package"] = "Trade"
            self.cpp_info.components["trade"].names["cmake_find_package_multi"] = "Trade"
            self.cpp_info.components["trade"].libs = ["MagnumTrade"]
            self.cpp_info.components["trade"].requires = ["magnum_main", "corrade::plugin_manager"]

        # VK
        if self.options.with_vk:
            self.cpp_info.components["vk"].names["cmake_find_package"] = "Vk"
            self.cpp_info.components["vk"].names["cmake_find_package_multi"] = "Vk"
            self.cpp_info.components["vk"].libs = ["MagnumVk"]
            self.cpp_info.components["vk"].requires = ["magnum_main", "vulkan-loader::vulkan-loader"]

        if self.options.get_safe("with_cglcontext", False):
            self.cpp_info.components["cglcontext"].names["cmake_find_package"] = "CglContext"
            self.cpp_info.components["cglcontext"].names["cmake_find_package_multi"] = "CglContext"
            self.cpp_info.components["cglcontext"].libs = ["MagnumCglContext"]
            self.cpp_info.components["cglcontext"].requires = ["magnum_main", "gl"]
        
            # FIXME: If only one *context is provided, then it also gets the GLContext alias
            self.cpp_info.components["glcontext"].names["cmake_find_package"] = "GLContext"
            self.cpp_info.components["glcontext"].names["cmake_find_package_multi"] = "GLContext"
            self.cpp_info.components["glcontext"].requires = ["cglcontext"]

        ######## PLUGINS ########
        # If shared, there are no libraries to link with
        if self.options.with_anyimageimporter:
            self.cpp_info.components["anyimageimporter"].names["cmake_find_package"] = "AnyImageImporter"
            self.cpp_info.components["anyimageimporter"].names["cmake_find_package_multi"] = "AnyImageImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anyimageimporter"].libs = ["AnyImageImporter"]
                self.cpp_info.components["anyimageimporter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'importers')]
            self.cpp_info.components["anyimageimporter"].requires = ["trade"]

        if self.options.with_anyimageconverter:
            self.cpp_info.components["anyimageconverter"].names["cmake_find_package"] = "AnyImageConverter"
            self.cpp_info.components["anyimageconverter"].names["cmake_find_package_multi"] = "AnyImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anyimageconverter"].libs = ["AnyImageConverter"]
                self.cpp_info.components["anyimageconverter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'imageconverters')]
            self.cpp_info.components["anyimageconverter"].requires = ["trade"]

        if self.options.with_anysceneconverter:
            self.cpp_info.components["anysceneconverter"].names["cmake_find_package"] = "AnySceneConverter"
            self.cpp_info.components["anysceneconverter"].names["cmake_find_package_multi"] = "AnySceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anysceneconverter"].libs = ["AnySceneConverter"]
                self.cpp_info.components["anysceneconverter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'sceneconverters')]
            self.cpp_info.components["anysceneconverter"].requires = ["trade"]

        if self.options.with_anysceneimporter:
            self.cpp_info.components["anysceneimporter"].names["cmake_find_package"] = "AnySceneImporter"
            self.cpp_info.components["anysceneimporter"].names["cmake_find_package_multi"] = "AnySceneImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["anysceneimporter"].libs = ["AnySceneImporter"]
                self.cpp_info.components["anysceneimporter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'importers')]
            self.cpp_info.components["anysceneimporter"].requires = ["trade"]

        if self.options.with_magnumfont:
            self.cpp_info.components["magnumfont"].names["cmake_find_package"] = "MagnumFont"
            self.cpp_info.components["magnumfont"].names["cmake_find_package_multi"] = "MagnumFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["magnumfont"].libs = ["MagnumFont"]
                self.cpp_info.components["magnumfont"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'fonts')]
            self.cpp_info.components["magnumfont"].requires = ["magnum_main", "trade", "text"]

        if self.options.with_magnumfontconverter:
            self.cpp_info.components["magnumfontconverter"].names["cmake_find_package"] = "MagnumFontConverter"
            self.cpp_info.components["magnumfontconverter"].names["cmake_find_package_multi"] = "MagnumFontConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["magnumfontconverter"].libs = ["MagnumFontConverter"]
                self.cpp_info.components["magnumfontconverter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'fontconverters')]
            self.cpp_info.components["magnumfontconverter"].requires = ["magnum_main", "trade", "text"]
            if not self.options.shared_plugins:
                self.cpp_info.components["magnumfontconverter"].requires += ["tgaimageconverter"]

        if self.options.with_objimporter:
            self.cpp_info.components["objimporter"].names["cmake_find_package"] = "ObjImporter"
            self.cpp_info.components["objimporter"].names["cmake_find_package_multi"] = "ObjImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["objimporter"].libs = ["ObjImporter"]
                self.cpp_info.components["objimporter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'importers')]
            self.cpp_info.components["objimporter"].requires = ["trade", "meshtools"]

        if self.options.with_tgaimageconverter:
            self.cpp_info.components["tgaimageconverter"].names["cmake_find_package"] = "TgaImageConverter"
            self.cpp_info.components["tgaimageconverter"].names["cmake_find_package_multi"] = "TgaImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["tgaimageconverter"].libs = ["TgaImageConverter"]
                self.cpp_info.components["tgaimageconverter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'imageconverters')]
            self.cpp_info.components["tgaimageconverter"].requires = ["trade"]

        if self.options.with_tgaimporter:
            self.cpp_info.components["tgaimporter"].names["cmake_find_package"] = "TgaImporter"
            self.cpp_info.components["tgaimporter"].names["cmake_find_package_multi"] = "TgaImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["tgaimporter"].libs = ["TgaImporter"]
                self.cpp_info.components["tgaimporter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'importers')]
            self.cpp_info.components["tgaimporter"].requires = ["trade"]
