from conan import ConanFile, tools
from conans import CMake
import functools

required_conan_version = ">=1.33.0"

class ImplotConan(ConanFile):
    name = "implot"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/epezent/implot"
    description = "Advanced 2D Plotting for Dear ImGui"
    topics = ("imgui", "plot", "graphics", )
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    options = {
        "shared": [True, False],
         "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

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
        if tools.scm.Version(self.version) >= "0.13":
            self.requires("imgui/1.87")
        else:
            self.requires("imgui/1.86")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["implot"]
