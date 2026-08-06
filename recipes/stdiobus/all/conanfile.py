from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
import os


class StdioBusCppConan(ConanFile):
    name = "stdiobus"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stdiobus/stdiobus-cpp"
    description = "C++17 SDK for stdio Bus - AI agent transport layer for MCP/ACP protocols"
    topics = ("stdiobus", "mcp", "acp", "agent", "transport", "json-rpc", "ipc")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False], "exceptions": [True, False]}
    default_options = {"fPIC": True, "exceptions": False}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("stdiobus does not support Windows")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STDIOBUS_CPP_EXCEPTIONS"] = bool(self.options.exceptions)
        tc.variables["STDIOBUS_BUILD_TESTS"] = False
        tc.variables["STDIOBUS_BUILD_EXAMPLES"] = False
        tc.variables["STDIOBUS_BUILD_BENCHMARKS"] = False
        tc.variables["STDIOBUS_BUILD_FUZZ"] = False
        tc.variables["STDIOBUS_INSTALL"] = True
        tc.variables["STDIOBUS_WARNINGS_AS_ERRORS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "stdiobus")
        self.cpp_info.set_property("cmake_target_name", "stdiobus::stdiobus")
        self.cpp_info.set_property("pkg_config_name", "stdiobus")
        self.cpp_info.libs = ["stdiobus", "stdio_bus"]
        if self.options.exceptions:
            self.cpp_info.defines.append("STDIOBUS_CPP_EXCEPTIONS=1")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
