from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0"


class CxxmcpConan(ConanFile):
    name = "cxxmcp"
    description = "C++ MCP SDK for protocol, client, server, transport, peer, and handler APIs."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/caomengxuan666/cxxmcp"
    topics = ("mcp", "model-context-protocol", "json-rpc", "sdk")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpp-httplib/0.45.0", transitive_headers=True, transitive_libs=True)
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)
        self.requires("tl-expected/1.2.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["CXXMCP_BUILD_SDK"] = True
        tc.variables["CXXMCP_BUILD_RUNTIME"] = False
        tc.variables["CXXMCP_BUILD_APP"] = False
        tc.variables["CXXMCP_BUILD_GATEWAY"] = False
        tc.variables["CXXMCP_BUILD_CLI"] = False
        tc.variables["CXXMCP_BUILD_EXAMPLES"] = False
        tc.variables["CXXMCP_BUILD_TESTS"] = False
        tc.variables["CXXMCP_BUILD_DOCS"] = False
        tc.variables["CXXMCP_USE_SYSTEM_DEPS"] = True
        tc.variables["BUILD_SHARED_LIBS"] = False
        if self.settings.os != "Windows":
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cxxmcp")

        self.cpp_info.components["core"].set_property("cmake_target_name", "cxxmcp::core")
        self.cpp_info.components["core"].requires = ["tl-expected::expected"]

        self.cpp_info.components["jsonrpcpp"].set_property("cmake_target_name", "cxxmcp::jsonrpcpp")
        self.cpp_info.components["jsonrpcpp"].requires = ["nlohmann_json::nlohmann_json"]

        self.cpp_info.components["protocol"].set_property("cmake_target_name", "cxxmcp::protocol")
        self.cpp_info.components["protocol"].libs = ["mcp_protocol"]
        self.cpp_info.components["protocol"].requires = [
            "core",
            "jsonrpcpp",
            "nlohmann_json::nlohmann_json",
        ]

        self.cpp_info.components["transport"].set_property("cmake_target_name", "cxxmcp::transport")
        self.cpp_info.components["transport"].requires = ["protocol"]

        self.cpp_info.components["client"].set_property("cmake_target_name", "cxxmcp::client")
        self.cpp_info.components["client"].libs = ["mcp_client"]
        self.cpp_info.components["client"].requires = [
            "transport",
            "cpp-httplib::cpp-httplib",
        ]

        self.cpp_info.components["server"].set_property("cmake_target_name", "cxxmcp::server")
        self.cpp_info.components["server"].libs = ["mcp_server"]
        self.cpp_info.components["server"].requires = [
            "transport",
            "cpp-httplib::cpp-httplib",
        ]

        self.cpp_info.components["peer"].set_property("cmake_target_name", "cxxmcp::peer")
        self.cpp_info.components["peer"].requires = ["client", "server"]

        self.cpp_info.components["handler"].set_property("cmake_target_name", "cxxmcp::handler")
        self.cpp_info.components["handler"].requires = ["client", "server"]

        self.cpp_info.components["service"].set_property("cmake_target_name", "cxxmcp::service")
        self.cpp_info.components["service"].requires = ["peer"]

        self.cpp_info.components["sdk"].set_property("cmake_target_name", "cxxmcp::sdk")
        self.cpp_info.components["sdk"].requires = [
            "protocol",
            "client",
            "server",
            "transport",
            "peer",
            "handler",
            "service",
        ]

        self.cpp_info.components["plugin_sdk"].set_property("cmake_target_name", "cxxmcp::plugin_sdk")
        self.cpp_info.components["plugin_sdk"].requires = ["protocol"]

        self.cpp_info.components["adapters"].set_property("cmake_target_name", "cxxmcp::adapters")
        self.cpp_info.components["adapters"].requires = ["server", "plugin_sdk"]
