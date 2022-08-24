from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class BitserializerConan(ConanFile):
    name = "bitserializer"
    description = "C++ 17 library for serialization to multiple output formats (JSON, XML, YAML)"
    topics = ("serialization", "json", "xml")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/Pavel_Kisliak/bitserializer"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_cpprestsdk": [True, False],
        "with_rapidjson": [True, False],
        "with_pugixml": [True, False],
    }
    default_options = {
        "with_cpprestsdk": False,
        "with_rapidjson": False,
        "with_pugixml": False,
    }

    no_copy_source = True

    @property
    def _supported_compilers(self):
        if tools.Version(self.version) >= "0.44":
            return {
                "gcc": "8",
                "clang": "8",
                "Visual Studio": "15",
                "apple-clang": "12",
            }

        return {
            "gcc": "8",
            "clang": "7",
            "Visual Studio": "15",
            "apple-clang": "12",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_cpprestsdk:
            self.requires("cpprestsdk/2.10.18")
        if self.options.with_rapidjson:
            self.requires("rapidjson/cci.20211112")
        if self.options.with_pugixml:
            self.requires("pugixml/1.11")

    def validate(self):
        # Check compiler for supporting C++ 17
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "17")
        try:
            minimum_required_compiler_version = self._supported_compilers[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

        # Check stdlib ABI compatibility
        compiler_name = str(self.settings.compiler)
        if compiler_name == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration('Using %s with GCC requires "compiler.libcxx=libstdc++11"' % self.name)
        elif compiler_name == "clang" and self.settings.compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration('Using %s with Clang requires either "compiler.libcxx=libstdc++11"'
                                            ' or "compiler.libcxx=libc++"' % self.name)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "bitserializer")

        # cpprestjson-core
        self.cpp_info.components["bitserializer-core"].set_property("cmake_target_name", "BitSerializer::core")
        if self.settings.compiler == "gcc" or (self.settings.os == "Linux" and self.settings.compiler == "clang"):
            if tools.Version(self.settings.compiler.version) < 9:
                self.cpp_info.components["bitserializer-core"].system_libs = ["stdc++fs"]

        # cpprestjson-archive
        if self.options.with_cpprestsdk:
            self.cpp_info.components["bitserializer-cpprestjson"].set_property("cmake_target_name", "BitSerializer::cpprestjson-archive")
            self.cpp_info.components["bitserializer-cpprestjson"].requires = ["bitserializer-core", "cpprestsdk::cpprestsdk"]

        # rapidjson-archive
        if self.options.with_rapidjson:
            self.cpp_info.components["bitserializer-rapidjson"].set_property("cmake_target_name", "BitSerializer::rapidjson-archive")
            self.cpp_info.components["bitserializer-rapidjson"].requires = ["bitserializer-core", "rapidjson::rapidjson"]

        # pugixml-archive
        if self.options.with_pugixml:
            self.cpp_info.components["bitserializer-pugixml"].set_property("cmake_target_name", "BitSerializer::pugixml-archive")
            self.cpp_info.components["bitserializer-pugixml"].requires = ["bitserializer-core", "pugixml::pugixml"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "bitserializer"
        self.cpp_info.filenames["cmake_find_package_multi"] = "bitserializer"
        self.cpp_info.names["cmake_find_package"] = "BitSerializer"
        self.cpp_info.names["cmake_find_package_multi"] = "BitSerializer"
        self.cpp_info.components["bitserializer-core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["bitserializer-core"].names["cmake_find_package_multi"] = "core"
        if self.options.with_cpprestsdk:
            self.cpp_info.components["bitserializer-cpprestjson"].names["cmake_find_package"] = "cpprestjson-archive"
            self.cpp_info.components["bitserializer-cpprestjson"].names["cmake_find_package_multi"] = "cpprestjson-archive"
        if self.options.with_rapidjson:
            self.cpp_info.components["bitserializer-rapidjson"].names["cmake_find_package"] = "rapidjson-archive"
            self.cpp_info.components["bitserializer-rapidjson"].names["cmake_find_package_multi"] = "rapidjson-archive"
        if self.options.with_pugixml:
            self.cpp_info.components["bitserializer-pugixml"].names["cmake_find_package"] = "pugixml-archive"
            self.cpp_info.components["bitserializer-pugixml"].names["cmake_find_package_multi"] = "pugixml-archive"
