
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
    exports_sources = "include/*", "CMakeLists.txt", "test/*", "doc/CMakeLists.txt", "doc/*.md"
    no_copy_source = True
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "SI-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            # Add additional settings with cmake.definitions["SOME_DEFINITION"] = True
            self._cmake.definitions["SI_BUILD_TESTING"] = "OFF"
            self._cmake.definitions["SI_BUILD_DOC"] = "OFF"
            self._cmake.definitions["SI_INSTALL_LIBRARY"] = "ON"
            self._cmake.configure(
                source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def test(self):
        cmake = self._configure_cmake()
        cmake.test()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        #  Remove folder containing cmake-specific files such as SIConfig.cmake and SIVersion.cmake
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
