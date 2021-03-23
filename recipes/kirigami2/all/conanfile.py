import os
import glob
from conans import ConanFile, CMake, tools


class Kirigami2Conan(ConanFile):
    name = "kirigami2"
    description = "Build beautiful, convergent apps that run on phones, TVs and everything in between."
    license = "LGPLv2"
    topics = ("conan", "gui", "qt")
    homepage = "https://develop.kde.org/frameworks/kirigami/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"
    requires = ["qt/5.15.2", "extra-cmake-modules/5.80.0"]
    exports_sources = "CMakeLists.txt"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("kirigami2*")[0]
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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
