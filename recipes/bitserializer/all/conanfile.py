from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


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
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7" if Version(self.version) < "0.44" else "8",
            "Visual Studio": "15",
            "msvc": "191",
            "apple-clang": "12",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_cpprestsdk:
            self.requires("cpprestsdk/2.10.18", transitive_headers=True, transitive_libs=True)
        if self.options.with_rapidjson:
            self.requires("rapidjson/cci.20220514", transitive_headers=True, transitive_libs=True)
        if self.options.with_pugixml:
            self.requires("pugixml/1.13", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        # Check stdlib ABI compatibility
        compiler_name = str(self.settings.compiler)
        if compiler_name == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(f'Using {self.ref} with GCC requires "compiler.libcxx=libstdc++11"')
        elif compiler_name == "clang" and self.settings.compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration(f'Using {self.ref} with Clang requires either "compiler.libcxx=libstdc++11"'
                                            ' or "compiler.libcxx=libc++"')

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "license.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "bitserializer")

        # cpprestjson-core
        self.cpp_info.components["bitserializer-core"].set_property("cmake_target_name", "BitSerializer::core")
        self.cpp_info.components["bitserializer-core"].bindirs = []
        self.cpp_info.components["bitserializer-core"].libdirs = []
        if self.settings.compiler == "gcc" or (self.settings.os == "Linux" and self.settings.compiler == "clang"):
            if Version(self.settings.compiler.version) < 9:
                self.cpp_info.components["bitserializer-core"].system_libs = ["stdc++fs"]

        # cpprestjson-archive
        if self.options.with_cpprestsdk:
            self.cpp_info.components["bitserializer-cpprestjson"].set_property("cmake_target_name", "BitSerializer::cpprestjson-archive")
            self.cpp_info.components["bitserializer-cpprestjson"].bindirs = []
            self.cpp_info.components["bitserializer-cpprestjson"].libdirs = []
            self.cpp_info.components["bitserializer-cpprestjson"].requires = ["bitserializer-core", "cpprestsdk::cpprestsdk"]

        # rapidjson-archive
        if self.options.with_rapidjson:
            self.cpp_info.components["bitserializer-rapidjson"].set_property("cmake_target_name", "BitSerializer::rapidjson-archive")
            self.cpp_info.components["bitserializer-rapidjson"].bindirs = []
            self.cpp_info.components["bitserializer-rapidjson"].libdirs = []
            self.cpp_info.components["bitserializer-rapidjson"].requires = ["bitserializer-core", "rapidjson::rapidjson"]

        # pugixml-archive
        if self.options.with_pugixml:
            self.cpp_info.components["bitserializer-pugixml"].set_property("cmake_target_name", "BitSerializer::pugixml-archive")
            self.cpp_info.components["bitserializer-pugixml"].bindirs = []
            self.cpp_info.components["bitserializer-pugixml"].libdirs = []
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
