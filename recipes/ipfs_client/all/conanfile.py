from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os


required_conan_version = ">=2"


class IpfsChromium(ConanFile):
    name = "ipfs_client"
    description = "Library for acting as a trustless client of IFPS gateway"
    homepage = "https://github.com/little-bear-labs/ipfs-chromium"
    topics = ("ipfs", "ipns", "dweb", "web", "content-addressed", "network", "client", "io", "api", "file-sharing", "gateway", "kubo")
    license = ("MIT", "Apache-2.0")
    url = 'https://github.com/conan-io/conan-center-index'
    settings = "os", "compiler", "build_type", "arch"
    package_type = 'static-library'
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "14",
            "clang": "9",
            "gcc": "11",
            "msvc": "193",
            "Visual Studio": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.85.0", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("c-ares/[>=1.27 <2]")
        self.requires("nlohmann_json/3.11.3")
        self.requires("protobuf/3.21.12", transitive_headers=True)
        # Let protobuf pick the specific version
        self.requires("abseil/[>=20240116.1 <20240117.0]")

    def validate(self):
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
        tc = CMakeToolchain(self)
        tc.cache_variables["INSIDE_CONAN"] = True
        cppstd = self.settings.get_safe("compiler.cppstd", self._min_cppstd).replace("gnu", "")
        if cppstd:
            tc.cache_variables["CXX_VERSION"] = cppstd
        # Disable testing discovery if installed in the system
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_GTest"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "library"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["proto"].libs = ["ic_proto"]
        self.cpp_info.components["proto"].requires = ["protobuf::protobuf"]

        self.cpp_info.components["client"].libs = ["ipfs_client"]
        self.cpp_info.components["client"].requires = [
            "proto",
            "protobuf::libprotobuf",
            "c-ares::c-ares",
            "abseil::absl_statusor",
            "boost::headers",
            "openssl::openssl",
            "nlohmann_json::nlohmann_json",
        ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["client"].system_libs = ["m"]
        self.cpp_info.components["client"].defines = ["HAS_BOOST_BEAST=1", "HAS_ARES=1", "HAS_OPENSSL_EVP=1"]
