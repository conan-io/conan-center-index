from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.63"


class IpfsChromium(ConanFile):
    name = "ipfs-chromium"
    description = "Library for acting as a trustless client of IFPS gateway"
    homepage = "https://github.com/little-bear-labs/ipfs-chromium"
    topics = ("ipfs", "ipns", "dweb", "web", "content-addressed", "network", "client", "io", "api", "file-sharing", "gateway", "kubo")
    license = ("MIT", "Apache-2.0")
    url = 'https://github.com/conan-io/conan-center-index'
    settings = ["os", "compiler", "build_type", "arch"]
    package_type = 'static-library'

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "14",
            "clang": "9",
            "gcc": "11",
            "msvc": "193",
            "Visual Studio": "15",
        }

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("boost/1.85.0")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("bzip2/1.0.8")
        self.requires("c-ares/1.33.1")
        self.requires("nlohmann_json/3.11.3")
        self.requires("abseil/20240722.0")
        self.requires("protobuf/5.27.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["INSIDE_CONAN"] = True
        tc.generate()
        d = CMakeDeps(self)
        d.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.source_folder, "licenses"), src=os.path.join(self.source_folder, "library"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ipfs_client", "ic_proto"]
