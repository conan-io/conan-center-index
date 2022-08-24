import os

from conan.errors import ConanInvalidConfiguration
from conan import ConanFile, tools
from conan.tools.cmake import CMake

required_conan_version = ">=1.33.0"

class STTreeConan(ConanFile):
    name = "st_tree"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A fast and flexible c++ template class for tree data structures"
    topics = ("stl", "container", "data-structures")
    homepage = "https://github.com/erikerlandson/st_tree"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def package(self):
        self.copy("LICENSE", "licenses", self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "st_tree"
        self.cpp_info.filenames["cmake_find_package_multi"] = "st_tree"
