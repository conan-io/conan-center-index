from conans import ConanFile, CMake
import os
from conan.tools.files import get, copy

class MicroserviceEssentials(ConanFile):
    name = "microservice-essentials"
    version = "0.1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seboste/microservice-essentials"
    license = "MIT"    
    description = """microservice-essentials is a portable, independent C++ library that takes care of typical recurring concerns that occur in microservice development."""
    topics = ("microservices", "cloud-native", "request-handling")
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake_find_package_multi", "cmake"    
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_testing": [True, False],
        "build_examples": [True, False]        
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_testing": False,
        "build_examples": False
    }

    def requirements(self):
        if self.options.build_examples:
            self.requires("cpp-httplib/0.12.4")
            self.requires("nlohmann_json/3.11.2")
            self.requires("openssl/3.1.0")
            self.requires("grpc/1.50.1")
        if self.options.build_testing:
            self.requires("catch2/3.3.2")
            self.requires("nlohmann_json/3.11.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_TESTING'] = self.options.build_testing
        cmake.definitions['BUILD_EXAMPLES'] = self.options.build_examples
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["microservice-essentials"]
        if self.settings.os != "Windows":
            self.cpp_info.system_libs = ["pthread"]
