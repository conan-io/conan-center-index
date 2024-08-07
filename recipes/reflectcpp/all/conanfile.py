from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
import os

required_conan_version = ">=1.51.1"


class ReflectCppConan(ConanFile):
    name = "reflectcpp"
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

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cbor": [True, False],
        "with_flatbuffers": [True, False],
        "with_json": [True, False],
        "with_msgpack": [True, False],
        "with_toml": [True, False],
        "with_xml": [True, False],
        "with_yaml": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cbor": False,
        "with_flatbuffers": False,
        "with_json": True,
        "with_msgpack": False,
        "with_toml": False,
        "with_xml": False,
        "with_yaml": False,
    }
    src_folder = "src"
    build_requires = "cmake/3.30.1"

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "17",
            "msvc": "193",
            "gcc": "11.4",
            "clang": "16",
            "apple-clang": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(cli_args=["-DREFLECTCPP_USE_BUNDLED_DEPENDENCIES=OFF"])
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def requirements(self):
        self.requires("ctre/3.9.0", transitive_headers=True)
        if self.options.with_cbor:
            self.requires("tinycbor/0.6.0", transitive_headers=True)
        if self.options.with_flatbuffers:
            self.requires("flatbuffers/23.5.26", transitive_headers=True)
        if self.options.with_json:
            self.requires("yyjson/0.8.0", transitive_headers=True)
        if self.options.with_msgpack:
            self.requires("msgpack-c/6.0.0", transitive_headers=True)
        if self.options.with_toml:
            self.requires("tomlplusplus/3.4.0", transitive_headers=True)
        if self.options.with_xml:
            self.requires("pugixml/1.14", transitive_headers=True)
        if self.options.with_yaml:
            self.requires("yaml-cpp/0.8.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_info(self):
        self.cpp_info.libs = ["reflectcpp"]
