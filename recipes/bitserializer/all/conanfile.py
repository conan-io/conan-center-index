from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class BitserializerConan(ConanFile):
    name = "bitserializer"
    description = "C++17 serialization to JSON/JSONC, XML, YAML, CSV and MsgPack via one API, with self-contained built-in formats and optional fast_float acceleration."
    topics = ("c-plus-plus", "cpp17", "csv", "deserialization", "json", "jsonc", "messagepack", "msgpack", "serialization", "xml", "yaml")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/PavelKisliak/BitSerializer"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rapidjson": [True, False],
        "with_pugixml": [True, False],
        "with_rapidyaml": [True, False],
        "with_csv": [True, False],
        "with_msgpack": [True, False],
        "with_json": [True, False],
        "with_fast_float": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rapidjson": False,
        "with_pugixml": False,
        "with_rapidyaml": False,
        "with_csv": False,
        "with_msgpack": False,
        "with_json": False,
        "with_fast_float": True,
    }

    def _is_header_only(self, info=False):
        # All components are header-only except the compiled JSON, CSV and MsgPack archives.
        options = self.info.options if info else self.options
        return not (
            options.get_safe("with_json")
            or options.get_safe("with_csv")
            or options.get_safe("with_msgpack")
        )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.90":
            self.options.rm_safe("with_json")
            self.options.rm_safe("with_fast_float")

    def configure(self):
        if self._is_header_only():
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
            self.package_type = "header-library"

    def layout(self):
        if self._is_header_only():
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_rapidjson"):
            self.requires("rapidjson/1.1.0", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_pugixml"):
            # PugiXml declares the std::string_view overload in the header when the consumer
            # uses C++17, but its prebuilt library is compiled with an older standard.
            # Use the header-only package so declarations and definitions match.
            self.requires("pugixml/1.15", transitive_headers=True, transitive_libs=True,
                          options={"header_only": True})
        if self.options.get_safe("with_fast_float"):
            self.requires("fast_float/8.2.10", transitive_headers=True)
        if self.options.get_safe("with_rapidyaml"):
            # RapidYAML headers inline c4core code. The CCI rapidyaml recipe exposes the c4core
            # headers but does not propagate its libraries, so consumers that include the ryml
            # headers need c4core at link time as well.
            if Version(self.version) >= "0.90":
                self.requires("rapidyaml/[>=0.15.2 <0.17]", transitive_headers=True, transitive_libs=True)
                self.requires("c4core/0.4.0", transitive_headers=True, transitive_libs=True)
            else:
                self.requires("rapidyaml/[>=0.8.0 <=0.10.0]", transitive_headers=True, transitive_libs=True)
                self.requires("c4core/0.2.0", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        if self._is_header_only(info=True):
            fast_float = self.info.options.get_safe("with_fast_float")
            self.info.clear()
            if fast_float is not None:
                self.info.options.with_fast_float = fast_float

    def validate(self):
        check_min_cppstd(self, 17)

        # Check stdlib ABI compatibility
        compiler_name = str(self.settings.compiler)
        if compiler_name == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(f'Using {self.ref} with GCC requires "compiler.libcxx=libstdc++11"')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        if not self._is_header_only():
            tc = CMakeToolchain(self)
            for option, cache_variable in (
                ("with_rapidjson", "BUILD_RAPIDJSON_ARCHIVE"),
                ("with_pugixml", "BUILD_PUGIXML_ARCHIVE"),
                ("with_rapidyaml", "BUILD_RAPIDYAML_ARCHIVE"),
                ("with_csv", "BUILD_CSV_ARCHIVE"),
                ("with_msgpack", "BUILD_MSGPACK_ARCHIVE"),
                ("with_json", "BUILD_JSON_ARCHIVE"),
            ):
                value = self.options.get_safe(option)
                if value is not None:
                    tc.cache_variables[cache_variable] = value
            if self.options.get_safe("with_fast_float") is False:
                tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_FastFloat"] = True
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()

    def _patch_sources(self):
        # BitSerializer 0.90 and later detect both ryml.hpp layouts with __has_include.
        # Older releases only include "ryml/..." and need the path flattened.
        if Version(self.version) < "0.90":
            replace_in_file(
                self,
                os.path.join(self.source_folder, "include", "bitserializer", "rapidyaml_archive.h"),
                "#include \"ryml/",
                "#include \"",
            )

    def build(self):
        if not self._is_header_only():
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        if not self._is_header_only():
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
        else:
            copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        # Copy license
        copy(self, "license.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        lib_suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.set_property("cmake_file_name", "bitserializer")

        # bitserializer-core
        core = self.cpp_info.components["bitserializer-core"]
        core.set_property("cmake_target_name", "BitSerializer::core")
        core.bindirs = []
        core.libdirs = []
        if self.options.get_safe("with_fast_float"):
            core.requires = ["fast_float::fast_float"]
            core.defines = ["BITSERIALIZER_HAS_FAST_FLOAT=1"]
        if self.settings.compiler == "gcc" or (self.settings.os == "Linux" and self.settings.compiler == "clang"):
            if Version(self.settings.compiler.version) < 9:
                core.system_libs = ["stdc++fs"]

        # rapidjson-archive
        if self.options.get_safe("with_rapidjson"):
            self.cpp_info.components["bitserializer-rapidjson"].set_property("cmake_target_name", "BitSerializer::rapidjson-archive")
            self.cpp_info.components["bitserializer-rapidjson"].bindirs = []
            self.cpp_info.components["bitserializer-rapidjson"].libdirs = []
            self.cpp_info.components["bitserializer-rapidjson"].requires = ["bitserializer-core", "rapidjson::rapidjson"]

        # pugixml-archive
        if self.options.get_safe("with_pugixml"):
            self.cpp_info.components["bitserializer-pugixml"].set_property("cmake_target_name", "BitSerializer::pugixml-archive")
            self.cpp_info.components["bitserializer-pugixml"].bindirs = []
            self.cpp_info.components["bitserializer-pugixml"].libdirs = []
            self.cpp_info.components["bitserializer-pugixml"].requires = ["bitserializer-core", "pugixml::pugixml"]

        # rapidyaml-archive
        if self.options.get_safe("with_rapidyaml"):
            self.cpp_info.components["bitserializer-rapidyaml"].set_property("cmake_target_name", "BitSerializer::rapidyaml-archive")
            self.cpp_info.components["bitserializer-rapidyaml"].bindirs = []
            self.cpp_info.components["bitserializer-rapidyaml"].libdirs = []
            self.cpp_info.components["bitserializer-rapidyaml"].requires = ["bitserializer-core", "rapidyaml::rapidyaml", "c4core::c4core"]

        # json-archive
        if self.options.get_safe("with_json"):
            self.cpp_info.components["bitserializer-json"].set_property("cmake_target_name", "BitSerializer::json-archive")
            self.cpp_info.components["bitserializer-json"].requires = ["bitserializer-core"]
            self.cpp_info.components["bitserializer-json"].libs = [f"bitserializer-json{lib_suffix}"]

        # csv-archive
        if self.options.get_safe("with_csv"):
            self.cpp_info.components["bitserializer-csv"].set_property("cmake_target_name", "BitSerializer::csv-archive")
            self.cpp_info.components["bitserializer-csv"].requires = ["bitserializer-core"]
            self.cpp_info.components["bitserializer-csv"].libs = [f"bitserializer-csv{lib_suffix}"]

        # msgpack-archive
        if self.options.get_safe("with_msgpack"):
            self.cpp_info.components["bitserializer-msgpack"].set_property("cmake_target_name", "BitSerializer::msgpack-archive")
            self.cpp_info.components["bitserializer-msgpack"].requires = ["bitserializer-core"]
            self.cpp_info.components["bitserializer-msgpack"].libs = [f"bitserializer-msgpack{lib_suffix}"]
