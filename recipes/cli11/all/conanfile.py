from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"

class CLI11Conan(ConanFile):
    name = "cli11"
    homepage = "https://github.com/CLIUtils/CLI11"
    description = "A command line parser for C++11 and beyond."
    topics = ("cli-parser", "cpp11", "no-dependencies", "cli", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["CLI11_BUILD_EXAMPLES"] = False
        cmake.definitions["CLI11_BUILD_TESTS"] = False
        cmake.definitions["CLI11_BUILD_DOCS"] = False
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # since 2.1.1
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "CLI11::CLI11")
        self.cpp_info.set_property("cmake_file_name", "CLI11")
        self.cpp_info.set_property("pkg_config_name", "CLI11")
        self.cpp_info.names["cmake_find_package"] = "CLI11"
        self.cpp_info.names["cmake_find_package_multi"] = "CLI11"
        self.cpp_info.names["pkg_config"] = "CLI11"
