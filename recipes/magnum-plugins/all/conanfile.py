from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class MagnumConan(ConanFile):
    name = "magnum-plugins"
    description = "Plugins for the Magnum C++11/C++14 graphics engine"
    license = "MIT"
    topics = ("conan", "magnum", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        "with_assimpimporter": [True, False],
        
        "with_stbimageimporter": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        
        "with_assimpimporter": True,

        "with_stbimageimporter": True,
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
        self.requires("magnum/{}".format(self.version))

    #def build_requirements(self):
    #    self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if not self.options["magnum"].with_trade:
            raise ConanInvalidConfiguration("Magnum Trade is required")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        self._cmake.definitions["BUILD_PLUGINS_STATIC"] = not self.options.shared
        self._cmake.definitions["LIB_SUFFIX"] = ""
        self._cmake.definitions["BUILD_TESTS"] = False

        self._cmake.definitions["WITH_ASSIMPIMPORTER"] = self.options.with_assimpimporter

        self._cmake.definitions["WITH_STBIMAGEIMPORTER"] = self.options.with_stbimageimporter

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
        self.cpp_info.names["cmake_find_package"] = "MagnumPlugins"
        self.cpp_info.names["cmake_find_package_multi"] = "MagnumPlugins"

        if self.options.with_stbimageimporter:
            self.cpp_info.components["stbimageimporter"].names["cmake_find_package"] = "StbImageImporter"
            self.cpp_info.components["stbimageimporter"].names["cmake_find_package_multi"] = "StbImageImporter"
            self.cpp_info.components["stbimageimporter"].libs = ["StbImageImporter"]
            self.cpp_info.components["stbimageimporter"].requires = ["magnum::trade"]
