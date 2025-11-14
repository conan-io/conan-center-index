import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file

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
        check_min_cppstd(self, 20)
        # std::format requires:
        # - GCC 13+ (not available in GCC 11-12)
        # - Clang 14+
        # - MSVC 19.29+ (VS 2019 16.10+)
        if self.settings.compiler == "gcc":
            # Extract major version number for comparison
            gcc_version = str(self.settings.compiler.version)
            gcc_major = int(gcc_version.split('.')[0])
            if gcc_major < 13:
                raise ConanInvalidConfiguration(
                    f"influxdb-cpp-rest requires GCC 13+ for std::format support. "
                    f"Current version: {self.settings.compiler.version}"
                )
        elif self.settings.compiler == "clang":
            # Extract major version number for comparison
            clang_version = str(self.settings.compiler.version)
            clang_major = int(clang_version.split('.')[0])
            if clang_major < 14:
                raise ConanInvalidConfiguration(
                    f"influxdb-cpp-rest requires Clang 14+ for std::format support. "
                    f"Current version: {self.settings.compiler.version}"
                )
        elif self.settings.compiler == "msvc":
            # MSVC version is stored as "191", "192", etc. (19.1 = 191, 19.29 = 1929)
            # We need at least 192 (19.29)
            msvc_version = str(self.settings.compiler.version)
            msvc_numeric = int(msvc_version)
            if msvc_numeric < 192:
                raise ConanInvalidConfiguration(
                    f"influxdb-cpp-rest requires MSVC 19.29+ (VS 2019 16.10+) for std::format support. "
                    f"Current version: {self.settings.compiler.version}"
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
