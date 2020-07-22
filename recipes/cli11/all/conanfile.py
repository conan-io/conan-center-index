from conans import ConanFile, CMake, tools
import os


class CLI11Conan(ConanFile):
    name = "cli11"
    homepage = "https://github.com/CLIUtils/CLI11"
    description = "A command line parser for C++11 and beyond."
    topics = ("cli-parser", "cpp11", "no-dependencies", "cli", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BDS-3-Clause"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.upper() + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["CLI11_BUILD_EXAMPLES"] = False
        cmake.definitions["CLI11_BUILD_TESTS"] = False
        cmake.definitions["CLI11_BUILD_DOCS"] = False
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CLI11"
        self.cpp_info.names["cmake_find_package_multi"] = "CLI11"
