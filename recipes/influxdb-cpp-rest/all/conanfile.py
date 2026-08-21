import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file

required_conan_version = ">=2.9"


class InfluxdbCppRestConan(ConanFile):
    name = "influxdb-cpp-rest"
    description = "A C++ client library for InfluxDB using C++ REST SDK"
    package_type = "static-library"
    topics = ("influxdb", "cpprest", "http", "client")
    license = "MPL-2.0"
    homepage = "https://github.com/d-led/influxdb-cpp-rest"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("cpprestsdk/2.10.19")
        self.requires("rxcpp/4.1.1", transitive_headers=True)
        self.requires("openssl/[>=1.1 <4]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD", "#set(CMAKE_CXX_STANDARD")

    def validate(self):
        check_min_cppstd(self, 20)

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
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "influxdb-cpp-rest")

        # C++ client library (static)
        self.cpp_info.components["cpp-rest"].set_property("cmake_target_name", "influxdb-cpp-rest::influxdb-cpp-rest")
        self.cpp_info.components["cpp-rest"].libs = ["influxdb-cpp-rest"]
        self.cpp_info.components["cpp-rest"].includedirs = ["include/influxdb-cpp-rest"]
        self.cpp_info.components["cpp-rest"].requires = ["cpprestsdk::cpprest", "rxcpp::rxcpp", "openssl::openssl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["cpp-rest"].system_libs = ["pthread"]

        # C wrapper (shared)
        self.cpp_info.components["c-rest"].set_property("cmake_target_name", "influxdb-cpp-rest::influx-c-rest")
        self.cpp_info.components["c-rest"].libs = ["influx-c-rest"]
        self.cpp_info.components["c-rest"].includedirs = ["include/influx-c-rest"]
        self.cpp_info.components["c-rest"].requires = ["cpp-rest"]
        self.cpp_info.components["c-rest"].type = "shared-library"
        # Adding the "bin" folder to work around this https://github.com/conan-io/conan/issues/20222
        self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))
