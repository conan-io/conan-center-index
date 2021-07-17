from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class MagnumConan(ConanFile):
    name = "magnum"
    description = "Magnum — Lightweight and modular C++11/C++14 graphics middleware for games and data visualization"
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

        "with_anyimageimporter": [True, False],
        "with_anyimageconverter": [True, False],
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
        "with_vk": False,

        "with_anyimageimporter": True,
        "with_anyimageconverter": True,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
    
    def requirements(self):
        self.requires("corrade/{}".format(self.version))
        if self.options.with_gl:
            self.requires("opengl/system")
        if self.options.sdl2_application:
            self.requires("sdl/2.0.14")

    def build_requirements(self):
        self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if self.options.shared and not self.options["corrade"].shared:
            # To fix issue with resource management, see here: https://github.com/mosra/magnum/issues/304#issuecomment-451768389
            raise ConanInvalidConfiguration("If using 'shared=True', corrado should be shared as well")

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

        ##### Plugins related #####
        self._cmake.definitions["BUILD_PLUGINS_STATIC"] = not self.options.shared  # TODO: Different option
        self._cmake.definitions["WITH_ANYIMAGEIMPORTER"] = self.options.with_anyimageimporter
        self._cmake.definitions["WITH_ANYIMAGECONVERTER"] = self.options.with_anyimageconverter

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

        #tools.rmdir(os.path.join(self.package_folder, "cmake"))
        #tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        #tools.rmdir(os.path.join(self.package_folder, "share"))

        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Magnum"
        self.cpp_info.names["cmake_find_package_multi"] = "Magnum"

        # Magnum contains just the main library
        self.cpp_info.components["magnum_main"].names["cmake_find_package"] = "Magnum"
        self.cpp_info.components["magnum_main"].names["cmake_find_package_multi"] = "Magnum"
        self.cpp_info.components["magnum_main"].libs = ["Magnum"]
        self.cpp_info.components["magnum_main"].requires = ["corrade::utility"]

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
        # TODO: target here, disabled by default

        ######## PLUGINS ########
        # TODO: If shared, there are no libraries to link with
        if self.options.with_anyimageimporter:
            self.cpp_info.components["anyimageimporter"].names["cmake_find_package"] = "AnyImageImporter"
            self.cpp_info.components["anyimageimporter"].names["cmake_find_package_multi"] = "AnyImageImporter"
            self.cpp_info.components["anyimageimporter"].libs = ["AnyImageImporter"]
            self.cpp_info.components["anyimageimporter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'importers')]
            self.cpp_info.components["anyimageimporter"].requires = ["trade"]

        if self.options.with_anyimageconverter:
            self.cpp_info.components["anyimageconverter"].names["cmake_find_package"] = "AnyImageConverter"
            self.cpp_info.components["anyimageconverter"].names["cmake_find_package_multi"] = "AnyImageConverter"
            self.cpp_info.components["anyimageconverter"].libs = ["AnyImageConverter"]
            self.cpp_info.components["anyimageconverter"].libdirs = [os.path.join(self.package_folder, 'lib', 'magnum', 'imageconverters')]
            self.cpp_info.components["anyimageconverter"].requires = ["trade"]
