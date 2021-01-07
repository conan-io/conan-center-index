import os

from conans import ConanFile, CMake, tools


class BackportCppRecipe(ConanFile):
    name = "backport-cpp"
    description = "An ongoing effort to bring modern C++ utilities to be compatible with C++11"
    topics = ("conan", "backport-cpp", "header-only", "backport")
    homepage = "https://github.com/bitwizeshift/BackportCpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    generators = "cmake"
    no_copy_source=True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "BackportCpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BACKPORT_COMPILE_UNIT_TESTS"] = False
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Backport"
        self.cpp_info.names["cmake_find_package_multi"] = "Backport"
