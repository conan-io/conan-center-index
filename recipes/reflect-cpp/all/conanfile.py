from conan import ConanFile
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=2.0.9"


class ReflectCppConan(ConanFile):
    name = "reflect-cpp"
    description = "C++-20 library for fast serialization, deserialization and validation using reflection"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getml/reflect-cpp"
    topics = (
        "reflection",
        "serialization",
        "memory",
        "cbor",
        "flatbuffers",
        "json",
        "msgpack",
        "toml",
        "xml",
        "yaml",
    )
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _compilers_minimum_version(self):
        # TODO: MSVC 19.38 is required, but ConanCenterIndex CI has update 6 installed.
        #       Update msvc to 193 when having the CI updated to the latest update.
        return {
            "msvc": "194",
            "gcc": "11",
            "clang": "13",
            "apple-clang": "15",
        }

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cbor": [True, False],
        "with_flatbuffers": [True, False],
        "with_msgpack": [True, False],
        "with_toml": [True, False],
        "with_ubjson": [True, False],
        "with_xml": [True, False],
        "with_yaml": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cbor": False,
        "with_flatbuffers": False,
        "with_msgpack": False,
        "with_toml": False,
        "with_ubjson": False,
        "with_xml": False,
        "with_yaml": False,
    }
    implements = ["auto_shared_fpic"]

    def requirements(self):
        self.requires("ctre/3.9.0", transitive_headers=True)
        # INFO: include/rfl/json/Writer.hpp includes yyjson.h
        # INFO: Transitive lib needed to avoid undefined reference to symbol 'yyjson_mut_doc_new'
        self.requires("yyjson/0.10.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_cbor:
            self.requires("tinycbor/0.6.0", transitive_headers=True)
        if self.options.with_flatbuffers:
            self.requires("flatbuffers/24.3.25", transitive_headers=True)
        if self.options.with_msgpack:
            self.requires("msgpack-c/6.0.0", transitive_headers=True)
        if self.options.with_toml:
            self.requires("tomlplusplus/3.4.0", transitive_headers=True)
        if self.options.with_ubjson:
            self.requires("jsoncons/0.176.0", transitive_headers=True)
        if self.options.with_xml:
            self.requires("pugixml/1.14", transitive_headers=True)
        if self.options.with_yaml:
            self.requires("yaml-cpp/0.8.0", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <4]")

    def validate(self):
        check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++20 features, which your compiler does not fully support.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # INFO: Let Conan handle the C++ standard used via settings.compiler.cppstd
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 20)", "")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        deps = CMakeDeps(self)
        if self.options.with_flatbuffers:
            deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["REFLECTCPP_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["REFLECTCPP_USE_BUNDLED_DEPENDENCIES"] = False
        tc.cache_variables["REFLECTCPP_USE_VCPKG"] = False
        tc.cache_variables["REFLECTCPP_CBOR"] = self.options.with_cbor
        tc.cache_variables["REFLECTCPP_FLEXBUFFERS"] = self.options.with_flatbuffers
        tc.cache_variables["REFLECTCPP_MSGPACK"] = self.options.with_msgpack
        tc.cache_variables["REFLECTCPP_TOML"] = self.options.with_toml
        tc.cache_variables["REFLECTCPP_XML"] = self.options.with_xml
        tc.cache_variables["REFLECTCPP_YAML"] = self.options.with_yaml
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["reflectcpp"]
        self.cpp_info.set_property("cmake_target_name", "reflectcpp::reflectcpp")
        self.cpp_info.set_property("cmake_file_name", "reflectcpp")
