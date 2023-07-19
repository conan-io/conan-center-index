import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class SplunkOpentelemetryConan(ConanFile):
    name = "splunk-opentelemetry-cpp"
    description = "Splunk's distribution of OpenTelemetry C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/signalfx/splunk-otel-cpp"
    topics = ("opentelemetry", "observability", "tracing")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opentelemetry-cpp/1.0.1", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Architecture not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPLUNK_CPP_EXAMPLES"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SplunkOpenTelemetry")
        self.cpp_info.set_property("cmake_target_name", "SplunkOpenTelemetry::SplunkOpenTelemetry")
        self.cpp_info.libs = ["SplunkOpenTelemetry"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "SplunkOpenTelemetry"
        self.cpp_info.names["cmake_find_package_multi"] = "SplunkOpenTelemetry"
