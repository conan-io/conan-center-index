
from conans import CMake, ConanFile, tools
import os


class SiConan(ConanFile):
    name = "si"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bernedom/SI"
    description = "A header only c++ library that provides type safety and user defined literals \
         for handling pyhsical values defined in the International System of Units."
    topics = ("physical units", "SI-unit-conversion",
              "cplusplus-library", "cplusplus-17")
    exports_sources = "include/*", "CMakeLists.txt", "test/*", "doc/CMakeLists.txt", "doc/*.md", "cmake/SIConfig.cmake.in"
    no_copy_source = True
    generators = "cmake", "txt", "cmake_find_package"
    build_requires = "Catch2/2.11.1@catchorg/stable"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "si-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        # Add additional settings with cmake.definitions["SOME_DEFINITION"] = True
        cmake.configure()
        return cmake

    
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def test(self):
        cmake = self._configure_cmake()
        cmake.test()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        self.info.header_only()
