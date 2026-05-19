import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class InfluxdbCppRestConan(ConanFile):
    name = "influxdb-cpp-rest"
    description = "A C++ client library for InfluxDB using C++ REST SDK"
    package_type = "library"
    topics = ("influxdb", "cpprest", "http", "client")
    license = "MPL-2.0"
    homepage = "https://github.com/d-led/influxdb-cpp-rest"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
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
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options["cpprestsdk"].shared = True

    def requirements(self):
        self.requires("cpprestsdk/2.10.19")
        self.requires("rxcpp/4.1.1")

    def build_requirements(self):
        # Only for tests - not linked to the library
        self.test_requires("catch2/3.11.0")
        self.tool_requires("cmake/[>=3.20]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD", "#set(CMAKE_CXX_STANDARD")

    def validate(self):
        # Require C++20 for std::format support
        check_min_cppstd(self, 20)

        # Require compilers new enough for std::format / <format> (and friends) to work
        minimum_compiler_versions = {"gcc": 13, "clang": 15, "apple-clang": 14, "msvc": 192}
        minimum_version = minimum_compiler_versions.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"Requires {self.settings.compiler} >= {minimum_version} for std::format support")

        # Apple libc++ only makes floating-point std::to_chars (used by std::format)
        # available starting macOS 13.3. Building this library with an older
        # deployment target fails in the standard headers, so declare that
        # configuration as unsupported instead of failing during compilation.
        if self.settings.os == "Macos":
            deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
            if deployment_target and Version(deployment_target) < "13.3":
                raise ConanInvalidConfiguration(
                    f"{self.name}/{self.version} requires MACOSX_DEPLOYMENT_TARGET >= 13.3 "
                    "because std::format uses floating-point std::to_chars, which is "
                    "unavailable on earlier macOS deployment targets."
                )


    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # Disable tests and demo for packaging
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_DEMO"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "influxdb-cpp-rest")
        self.cpp_info.set_property("cmake_target_name", "influxdb-cpp-rest::influxdb-cpp-rest")
        
        # Libraries to link
        self.cpp_info.libs = ["influxdb-cpp-rest"]
        
        # Include directories
        self.cpp_info.includedirs = ["include"]
        
        # System dependencies (if any)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
