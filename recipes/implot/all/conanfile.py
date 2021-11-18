from conans import ConanFile, CMake, tools
import os

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
    requires = "imgui/1.85"

    options = {
        "shared": [True, False],
         "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["implot"]
        
        self.cpp_info.set_property("cmake_file_name", "implot")
        self.cpp_info.set_property("cmake_target_name", "implot")
        self.cpp_info.set_property("pkg_config_name", "implot")
