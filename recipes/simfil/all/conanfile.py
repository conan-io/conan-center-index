from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, replace_in_file
import os

required_conan_version = ">=1.62.0"


class SimfilRecipe(ConanFile):
    name = "simfil"
    description = "simfil is a C++ 17 library and a language for querying structured map feature data. The library provides an efficient in-memory storage pool for map data, optimized for the simfil query language, along with a query interpreter to query the actual data."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Klebert-Engineering/simfil"
    license = "BSD 3-Clause"
    topics = ["query language"]

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_json": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_json": True,
    }

    exports_sources = "include/*", "src/*"

    def validate(self):
        check_min_cppstd(self, "20")

    def build_requirements(self):
        self.build_requires("cmake/3.28.1")

    def requirements(self):
        self.requires("sfl/1.2.4", transitive_headers=True)
        self.requires("fmt/10.2.1", transitive_headers=True)
        self.requires("bitsery/5.2.3", transitive_headers=True)
        if self.options.with_json:
            self.requires("nlohmann_json/3.11.2")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SIMFIL_CONAN"] = True
        tc.cache_variables["SIMFIL_SHARED"] = bool(self.options.get_safe("shared"))
        tc.cache_variables["SIMFIL_WITH_REPL"] = False
        tc.cache_variables["SIMFIL_WITH_COVERAGE"] = False
        tc.cache_variables["SIMFIL_WITH_TESTS"] = False
        tc.cache_variables["SIMFIL_WITH_EXAMPLES"] = False
        tc.cache_variables["SIMFIL_WITH_MODEL_JSON"] = bool(self.options.with_json)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["simfil"]
        self.cpp_info.set_property("cmake_target_name", "simfil::simfil")
