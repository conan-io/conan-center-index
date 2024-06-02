import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import is_msvc
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, save

required_conan_version = ">=1.53.0"


class SioclientConan(ConanFile):
    name = "sioclient"
    description = "C++11 implementation of Socket.IO client"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/socketio/socket.io-client-cpp"
    topics = ("websocket", "client")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            self.options.rm_safe("shared")
            self.package_type = "static-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("websocketpp/0.8.2")
        self.requires("asio/1.30.2")
        self.requires("rapidjson/cci.20230929")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_SUBMODULES"] = False
        tc.variables["BUILD_UNIT_TESTS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "asio asio::asio", "asio::asio")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sioclient")

        self.cpp_info.components["sioclient_"].set_property("cmake_target_name", "sioclient::sioclient")
        self.cpp_info.components["sioclient_"].libs = ["sioclient"]
        self.cpp_info.components["sioclient_"].requires = [
            "websocketpp::websocketpp",
            "asio::asio",
            "rapidjson::rapidjson",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["sioclient_"].system_libs.extend(["m", "pthread"])

        if self.options.with_openssl:
            self.cpp_info.components["sioclient_tls"].set_property("cmake_target_name", "sioclient::sioclient_tls")
            self.cpp_info.components["sioclient_tls"].libs = ["sioclient_tls"]
            self.cpp_info.components["sioclient_tls"].requires = [
                "websocketpp::websocketpp",
                "asio::asio",
                "rapidjson::rapidjson",
                "openssl::openssl",
            ]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sioclient_tls"].system_libs.extend(["m", "pthread"])
