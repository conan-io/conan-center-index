from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0"


class MockServicesConan(ConanFile):
    name = "mock-services"
    license = "MIT"
    url = "https://github.com/mpernia/mock-services"
    homepage = "https://github.com/mpernia/mock-services"
    description = (
        "mock-services is a C++11 library providing lightweight mock servers "
        "for testing purposes — REST, SOAP, FTP, MQTT, and (optionally) SFTP."
    )
    topics = ("mock", "server", "rest", "soap", "ftp", "mqtt", "testing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_sftp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_sftp": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpp-httplib/0.44.0")
        self.requires("pugixml/1.15")

    def validate(self):
        check_min_cppstd(self, "11")
        if self.options.with_sftp:
            raise ConanInvalidConfiguration(
                "SFTP server uses FetchContent which violates CCI sandbox rules. "
                "Set with_sftp=False (default)."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={
            "MOCK_SERVICES_BUILD_EXAMPLES": "OFF",
            "MOCK_SERVICES_BUILD_TESTS": "OFF",
        })
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mock-services"]
        self.cpp_info.set_property("cmake_file_name", "mock-services")
        self.cpp_info.set_property("cmake_target_name", "mock-services::mock-services")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        if not self.options.shared:
            self.cpp_info.defines.append("MOCK_SERVICES_STATIC_DEFINE")
