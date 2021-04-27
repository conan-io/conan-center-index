from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class CfgfileConan(ConanFile):
    name = "cfgfile"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/cfgfile.git"
    license = "MIT"
    description = "Header-only library for reading/saving configuration files with schema defined in sources."
    no_copy_source = True
    generators = "cmake"
    topics = ("conan", "cfgfile", "configuration")
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "10"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warn("Unknown compiler, assuming it supports at least C++14")
            return

        version = tools.Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration("cfgfile requires a compiler that supports at least C++14")

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
