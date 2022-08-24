import os

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


class R8brainFreeSrcConan(ConanFile):
    name = "r8brain-free-src"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/avaneev/r8brain-free-src"
    description = "High-quality pro audio sample rate converter / resampler C++ library"
    topics = ("audio", "sample-rate", "conversion", "audio-processing", "resampler")
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    
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
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("Shared r8brain-free-src cannot be built with Visual Studio")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_folder = "r8brain-free-src-version-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
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
        self.cpp_info.libs = ["r8brain"]
        
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
