from conans import ConanFile, CMake, tools
import os
import glob


class CfgfileConan(ConanFile):
    name = "cfgfile"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/cfgfile.git"
    license = "MIT"
    description = "Header-only library for reading/saving configuration files with schema defined in sources."
    exports = "cfgfile/*", "COPYING", "generator/*", "3rdparty/Args/Args/*.hpp"
    generators = "cmake"
    topics = ("conan", "cfgfile", "configuration")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="source_subfolder/generator")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=self._source_subfolder + "/cfgfile", dst="include/cfgfile")

    def package_info(self):
        self.cpp_info.includedirs = ["."]
        self.cpp_info.names["cmake_find_package"] = "cfgfile"
        self.cpp_info.names["cmake_find_package_multi"] = "cfgfile"
