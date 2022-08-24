import os

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.32.0"


class EntityXConan(ConanFile):
    name = "entityx"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alecthomas/entityx/"
    topics = ("entity", "c++11", "type-safe", "component", "conan")
    license = "MIT"
    description = "EntityX is an EC system that uses C++11 features to provide type-safe component management, event delivery, etc."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("entityx-" + self.version, self._source_subfolder)

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("entityx shared library does not export all symbols with Visual Studio")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENTITYX_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ENTITYX_BUILD_TESTING"] = False
        self._cmake.definitions["ENTITYX_RUN_BENCHMARKS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "entityx"
        debug = "-d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["entityx{}".format(debug)]
