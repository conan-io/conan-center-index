from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class TmxliteConan(ConanFile):
    name = "tmxlite"
    description = "A lightweight C++14 parsing library for tmx map files created with the Tiled map editor."
    license = "Zlib"
    topics = ("tmxlite", "tmx", "tiled-map", "parser")
    homepage = "https://github.com/fallahn/tmxlite"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "rtti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "rtti": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("miniz/2.1.0")
        self.requires("pugixml/1.11")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 not supported")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # unvendor miniz
        tools.files.rm(self, os.path.join(self._source_subfolder, "tmxlite", "src"), "miniz*")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "tmxlite", "src", "CMakeLists.txt"),
                              "${PROJECT_DIR}/miniz.c", "")
        # unvendor pugixml
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "tmxlite", "src", "detail"))
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "tmxlite", "src", "CMakeLists.txt"),
                              "${PROJECT_DIR}/detail/pugixml.cpp", "")
        # Don't inject -O3 in compile flags
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "tmxlite", "CMakeLists.txt"),
                              "-O3", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TMXLITE_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["PROJECT_STATIC_RUNTIME"] = False
        self._cmake.definitions["USE_RTTI"] = self.options.rtti
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        if not self.options.shared:
            self.cpp_info.defines.append("TMXLITE_STATIC")
        if self.settings.os == "Android":
            self.cpp_info.system_libs.append("log", "android")
