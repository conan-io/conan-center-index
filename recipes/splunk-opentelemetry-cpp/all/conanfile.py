import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.scm import Version

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
        "build_jaeger_exporter": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_jaeger_exporter": True,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opentelemetry-cpp/1.8.3", transitive_headers=True) # v1.12 is not compatible
        self.requires("grpc/1.54.3")
        self.requires("nlohmann_json/3.11.3")
        if self.options.build_jaeger_exporter:
            self.requires("thrift/0.17.0")
            self.requires("libcurl/[>=7.78.0 <9]")

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"{self.settings.arch} architecture not supported")
        if self.options.build_jaeger_exporter and not self.dependencies["opentelemetry-cpp"].options.get_safe("with_jaeger"):
            raise ConanInvalidConfiguration("Cannot build Jaeger exporter without with_jaeger=True in opentelemetry-cpp")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPLUNK_CPP_TESTS"] = False
        tc.variables["SPLUNK_CPP_EXAMPLES"] = False
        tc.variables["SPLUNK_CPP_WITH_JAEGER_EXPORTER"] = self.options.build_jaeger_exporter
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
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
