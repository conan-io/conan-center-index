from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.28.0"

class BitserializerConan(ConanFile):
    name = "bitserializer"
    description = "C++ 17 library for serialization to multiple output formats (JSON, XML, YAML)"
    topics = ("serialization", "json", "xml")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/Pavel_Kisliak/bitserializer"
    license = "MIT"
    settings = "os", "compiler"
    no_copy_source = True
    options = {
        "with_cpprestsdk": [True, False],
        "with_rapidjson": [True, False],
        "with_pugixml": [True, False]
    }
    default_options = {
        "with_cpprestsdk": True,
        "with_rapidjson": True,
        "with_pugixml": True
    }

    @property
    def _supported_compilers(self):
        return {
            "gcc": "8",
            "clang": "7",
            "Visual Studio": "15",
            "apple-clang": "10",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")
        try:
            minimum_required_compiler_version = self._supported_compilers[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def requirements(self):
        if self.options.with_cpprestsdk:
            self.requires("cpprestsdk/2.10.16")
        if self.options.with_rapidjson:
            self.requires("rapidjson/1.1.0")
        if self.options.with_pugixml:
            self.requires("pugixml/1.10")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # Find and rename folder in the extracted sources
        # This workaround used in connection that zip-archive from BitBucket contains folder with some hash in name
        for dirname in os.listdir(self.source_folder):
            if "-bitserializer-" in dirname:
                os.rename(dirname, self._source_subfolder)
                break

    def package(self):
        self.copy(pattern="license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "bitserializer"
        self.cpp_info.filenames["cmake_find_package_multi"] = "bitserializer"
        self.cpp_info.names["cmake_find_package"] = "BitSerializer"
        self.cpp_info.names["cmake_find_package_multi"] = "BitSerializer"
        # core
        self.cpp_info.components["core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "core"
        if self.settings.compiler == "gcc" or (self.settings.os == "Linux" and self.settings.compiler == "clang"):
            if tools.Version(self.settings.compiler.version) < 9:
                self.cpp_info.components["core"].system_libs = ["stdc++fs"]
        # cpprestjson-archive
        if self.options.with_cpprestsdk:
            self.cpp_info.components["cpprestjson-archive"].requires = ["core", "cpprestsdk::cpprestsdk"]
        # rapidjson-archive
        if self.options.with_rapidjson:
            self.cpp_info.components["rapidjson-archive"].requires = ["core", "rapidjson::rapidjson"]
        # pugixml-archive
        if self.options.with_rapidjson:
            self.cpp_info.components["pugixml-archive"].requires = ["core", "pugixml::pugixml"]
