from conans import ConanFile, CMake
class MicroserviceEssentials(ConanFile):
    name = "microservice-essentials"
    version = "0.1.0"
    url = "https://github.com/seboste/microservice-essentials"
    license = "MIT"
    author = "Sebastian Steger (Sebastian.Steger@gmail.com)"
    description = """microservice-essentials is a portable, independent C++ library that takes care of typical recurring concerns that occur in microservice development."""
    settings = "os", "compiler", "build_type", "arch", "cppstd"    
    generators = "cmake_find_package_multi", "cmake"
    scm = {
        "type": "git",        
        "url": "https://github.com/seboste/microservice-essentials.git",
        "revision": "auto"
    }
    options = {
        "build_testing": [True, False],
        "build_examples": [True, False]        
    }
    default_options = {
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

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_TESTING'] = self.options.build_testing
        cmake.definitions['BUILD_EXAMPLES'] = self.options.build_examples
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["microservice-essentials"]
        if self.settings.os != "Windows":
            self.cpp_info.system_libs = ["pthread"]
    