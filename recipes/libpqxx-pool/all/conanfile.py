import os
from conan.tools.files import copy
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps

class PqxxPoolConan(ConanFile):
    name = "libpqxx_pool"
    version = "0.1.0"
    author = "quark punk"
    url = "https://github.com/quarkpunk/libpqxx-pool"
    description = "connection pool for pqxx library"
    topics = ("pqxx", "database", "postgresql", "connection-pool", "pool")
    license = "BSD-3-Clause"

    package_type = "library"
    generators = "CMakeDeps", "CMakeToolchain"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": False}
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def configure(self):
        self.options["libpqxx"].shared = True

    def requirements(self):
        self.requires("libpqxx/7.9.2")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*.hpp", self.source_folder, os.path.join(self.package_folder, "include"))
        copy(self, "*.lib", self.build_folder,  os.path.join(self.package_folder, "lib"))
        copy(self, "*.a",   self.build_folder,  os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libpqxx_pool")
        self.cpp_info.set_property("cmake_target_name", "libpqxx::pool")
        self.cpp_info.set_property("pkg_config_name", "libpqxx_pool")
        self.cpp_info.libs = ["libpqxx_pool"]
