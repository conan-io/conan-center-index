from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0"


class CxxmcpConan(ConanFile):
    name = "cxxmcp"
    description = "C++17 SDK for the Model Context Protocol."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/caomengxuan666/cxxmcp"
    topics = ("mcp", "model-context-protocol", "json-rpc", "sdk")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_http": [True, False],
        "with_websocket": [True, False],
        "with_auth": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_http": False,
        "with_websocket": False,
        "with_auth": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)
        self.requires("tl-expected/1.2.0", transitive_headers=True)
        if self.options.with_http or self.options.with_websocket:
            self.requires("cpp-httplib/0.45.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        http_enabled = bool(self.options.with_http) or bool(self.options.with_websocket)

        tc = CMakeToolchain(self)
        tc.variables["CXXMCP_BUILD_SDK"] = True
        tc.variables["CXXMCP_BUILD_EXAMPLES"] = False
        tc.variables["CXXMCP_BUILD_TESTS"] = False
        tc.variables["CXXMCP_BUILD_DOCS"] = False
        tc.variables["CXXMCP_ENABLE_HTTP"] = http_enabled
        tc.variables["CXXMCP_ENABLE_WEBSOCKET"] = bool(self.options.with_websocket)
        tc.variables["CXXMCP_ENABLE_AUTH"] = bool(self.options.with_auth)
        tc.variables["CXXMCP_USE_SYSTEM_DEPS"] = True
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
        http_enabled = bool(self.options.with_http) or bool(self.options.with_websocket)
        websocket_enabled = bool(self.options.with_websocket)
        optional_defines = []
        if http_enabled:
            optional_defines.append("CXXMCP_ENABLE_HTTP=1")
        if websocket_enabled:
            optional_defines.append("CXXMCP_ENABLE_WEBSOCKET=1")

        self.cpp_info.set_property("cmake_file_name", "cxxmcp")
        self.cpp_info.set_property("cmake_target_name", "cxxmcp::sdk")
        self.cpp_info.libs = ["mcp_server", "mcp_client", "mcp_protocol"]
        self.cpp_info.defines.extend(optional_defines)
        self._add_common_system_libs(self.cpp_info, http_enabled)

        self.cpp_info.components["core"].set_property("cmake_target_name", "cxxmcp::core")
        self.cpp_info.components["core"].requires = ["tl-expected::expected"]

        self.cpp_info.components["protocol"].set_property("cmake_target_name", "cxxmcp::protocol")
        self.cpp_info.components["protocol"].libs = ["mcp_protocol"]
        self.cpp_info.components["protocol"].requires = [
            "core",
            "nlohmann_json::nlohmann_json",
        ]

        self.cpp_info.components["transport"].set_property("cmake_target_name", "cxxmcp::transport")
        self.cpp_info.components["transport"].requires = ["protocol"]

        self.cpp_info.components["client"].set_property("cmake_target_name", "cxxmcp::client")
        self.cpp_info.components["client"].libs = ["mcp_client"]
        self.cpp_info.components["client"].requires = ["transport"]
        self.cpp_info.components["client"].defines.extend(optional_defines)
        self._add_common_system_libs(self.cpp_info.components["client"], http_enabled)

        self.cpp_info.components["server"].set_property("cmake_target_name", "cxxmcp::server")
        self.cpp_info.components["server"].libs = ["mcp_server"]
        self.cpp_info.components["server"].requires = ["transport"]
        self.cpp_info.components["server"].defines.extend(optional_defines)
        self._add_common_system_libs(self.cpp_info.components["server"], http_enabled)

        self.cpp_info.components["peer"].set_property("cmake_target_name", "cxxmcp::peer")
        self.cpp_info.components["peer"].requires = ["client", "server"]
        self.cpp_info.components["peer"].defines.extend(optional_defines)

        self.cpp_info.components["handler"].set_property("cmake_target_name", "cxxmcp::handler")
        self.cpp_info.components["handler"].requires = ["client", "server"]
        self.cpp_info.components["handler"].defines.extend(optional_defines)

        self.cpp_info.components["service"].set_property("cmake_target_name", "cxxmcp::service")
        self.cpp_info.components["service"].requires = ["peer"]
        self.cpp_info.components["service"].defines.extend(optional_defines)

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
        self.cpp_info.components["sdk"].defines.extend(optional_defines)

        if self.options.with_auth:
            self.cpp_info.components["auth"].set_property("cmake_target_name", "cxxmcp::auth")
            self.cpp_info.components["auth"].requires = [
                "core",
                "nlohmann_json::nlohmann_json",
            ]
            self.cpp_info.components["auth"].defines.append("CXXMCP_ENABLE_AUTH=1")
            self.cpp_info.components["client"].requires.append("auth")
            self.cpp_info.components["server"].requires.append("auth")
            self.cpp_info.components["sdk"].requires.append("auth")

    def _add_common_system_libs(self, cpp_info, http_enabled):
        if self.settings.os == "Windows" and http_enabled:
            cpp_info.system_libs.extend(["ws2_32", "crypt32"])
        elif self.settings.os in ("Linux", "FreeBSD"):
            cpp_info.system_libs.append("pthread")
