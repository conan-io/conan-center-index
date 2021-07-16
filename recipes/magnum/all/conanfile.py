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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "sdl2_application": True,
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
        #self.requires("opengl/system")
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

        self.cpp_info.components["_core"].libs = ["Magnum", "MagnumDebugTools", "MagnumGL",
                                                  "MagnumMeshTools", "MagnumPrimitives", 
                                                  "MagnumSceneGraph", "MagnumShaders",
                                                  "MagnumText", "MagnumTextureTool",
                                                  "MagnumTrade"]

        if self.options.sdl2_application:
            self.cpp_info.components["application"].names["cmake_find_package"] = "Application"
            self.cpp_info.components["application"].names["cmake_find_package_multi"] = "Application"
            self.cpp_info.components["application"].libs = ["MagnumSdl2Application"]
            self.cpp_info.components["application"].requires = ["_core", "sdl::sdl"]

        #self.cpp_info.libs = tools.collect_libs(self)
