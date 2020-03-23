import os

from conans import ConanFile, CMake, tools


class ConanRecipe(ConanFile):
    name = "catch2"
    description = "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    topics = ("conan", "catch2", "header-only", "unit-test", "tdd", "bdd")
    homepage = "https://github.com/catchorg/Catch2"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    no_copy_source=True
    
    _cmake = None
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"
    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Catch2-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = "OFF"
        self._cmake.definitions["CATCH_INSTALL_DOCS"] = "OFF"
        self._cmake.definitions["CATCH_INSTALL_HELPERS"] = "ON"
        self._cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder
        )
        return self._cmake

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        for cmake_file in ["ParseAndAddCatchTests.cmake", "Catch.cmake", "CatchAddTests.cmake"]:
            self.copy(cmake_file,
                      src=os.path.join(self._source_subfolder, "contrib"),
                      dst=os.path.join("lib", "cmake", "Catch2"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "Catch2")]
        self.cpp_info.names["cmake_find_package"] = "Catch2"
        self.cpp_info.names["cmake_find_package_multi"] = "Catch2"
