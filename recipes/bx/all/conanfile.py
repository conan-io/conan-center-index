import os
import glob
from conans import ConanFile, CMake, tools

class BxConan(ConanFile):
    name = "bx"
    description = "Base library used across multiple projects."
    license = "MIT"
    topics = ("conan", "bx")
    homepage = "https://github.com/bkaradzic/bx"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('bx-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "bx", "compat"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread", "rt"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["Foundation"]
