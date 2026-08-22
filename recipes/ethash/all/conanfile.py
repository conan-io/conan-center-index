from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class EthashConan(ConanFile):
    name = "ethash"
    description = "C/C++ implementation of Ethash and ProgPoW – the Ethereum Proof of Work algorithms"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chfast/ethash"
    topics = ("ethereum", "mining", "proof-of-work")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "build_ethash": [True, False],
               "build_global_context": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "build_ethash": True,
                       "build_global_context": True}

    @property
    def _min_cppstd(self):
        return 14

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.build_ethash:
            self.options.rm_safe("build_global_context")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "190",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "10",
        }

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.2 <4]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # INFO: Options are declared before project() call
        tc.cache_variables["ETHASH_INSTALL_CMAKE_CONFIG"] = False
        tc.cache_variables["ETHASH_TESTING"] = False
        tc.cache_variables["ETHASH_BUILD_ETHASH"] = self.options.build_ethash
        tc.cache_variables["ETHASH_BUILD_GLOBAL_CONTEXT"] = self.options.get_safe("build_global_context", False)
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
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["keccak"].set_property("cmake_target_name", "ethash::keccak")
        self.cpp_info.components["keccak"].libs = ["keccak"]

        if self.options.build_ethash:
            self.cpp_info.components["ethash"].set_property("cmake_target_name", "ethash::ethash")
            self.cpp_info.components["ethash"].requires = ["keccak"]
            self.cpp_info.components["ethash"].libs = ["ethash"]

        if self.options.get_safe("build_global_context"):
            # INFO: ethash-global-context is static library always
            self.cpp_info.components["global_context"].set_property("cmake_target_name", "ethash::global-context")
            self.cpp_info.components["global_context"].requires = ["ethash"]
            self.cpp_info.components["global_context"].libs = ["ethash-global-context"]
