from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.53.0"


class SimfilRecipe(ConanFile):
    name = "simfil"
    description = "simfil is a C++ 17 library and a language for querying structured map feature data. The library provides an efficient in-memory storage pool for map data, optimized for the simfil query language, along with a query interpreter to query the actual data."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Klebert-Engineering/simfil"
    license = "BSD-3-Clause"
    package_type = "library"
    topics = ["query-language", "json", "data-model"]

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

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "10",
            "clang": "10",
            "apple-clang": "14",
        }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        check_min_cppstd(self, 20)

        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires Concepts support. The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def build_requirements(self):
        self.tool_requires("cmake/[>3.19 <4]")

    def requirements(self):
        self.requires("sfl/1.2.4", transitive_headers=True)
        self.requires("fmt/10.0.0", transitive_headers=True)
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
        tc.cache_variables["SIMFIL_SHARED"] = self.options.get_safe("shared")
        tc.cache_variables["SIMFIL_WITH_REPL"] = False
        tc.cache_variables["SIMFIL_WITH_COVERAGE"] = False
        tc.cache_variables["SIMFIL_WITH_TESTS"] = False
        tc.cache_variables["SIMFIL_WITH_EXAMPLES"] = False
        tc.cache_variables["SIMFIL_WITH_MODEL_JSON"] = self.options.with_json
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
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["simfil"]
