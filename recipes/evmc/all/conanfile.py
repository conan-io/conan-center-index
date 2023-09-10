from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os


required_conan_version = ">=1.54.0"


class EVMCConan(ConanFile):
    name = "evmc"
    description = "EVMC – Ethereum Client-VM Connector API"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ethereum/evmc"
    topics = ("ethereum", "wasm", "evm")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    tool_requires = "cmake/[>=3.16.2 <4]"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "9",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EVMC_INSTALL"] = True
        tc.variables["EVMC_TESTING"] = False
        tc.variables["EVMC_JAVA"] = False
        tc.variables["EVMC_TESTING"] = False
        tc.variables["EVMC_EXAMPLES"] = False
        tc.variables["EVMC_TOOLS"] = False
        tc.variables["HUNTER_ENABLED"] = False
        tc.generate()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["evmc-instructions", "evmc-loader", "tooling"]
