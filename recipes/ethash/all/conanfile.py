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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _min_cppstd(self):
        return 20

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "11",
            "clang": "13",
            "apple-clang": "14.1",
        }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.2 <4]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["ETHASH_INSTALL_CMAKE_CONFIG"] = False
        tc.generate()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

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
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.components["keccak"].set_property("cmake_target_name", "keccak::keccak")
        self.cpp_info.components["keccak"].libs = ["keccak"]

        self.cpp_info.components["ethash"].set_property("cmake_target_name", "ethash::ethash")
        self.cpp_info.components["ethash"].requires = ["keccak"]
        self.cpp_info.components["ethash"].libs = ["ethash"]
