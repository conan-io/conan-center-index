from conans import ConanFile, CMake, tools
import os
import glob


class UTConan(ConanFile):
    name = "UT"
    description = "C++20 single header/single module, macro-free μ(micro)/Unit Testing Framework"
    topics = ("conan", "UT", "header-only", "unit-test", "tdd", "bdd")
    url = "https://github.com/boost-ext/ut"
    homepage = "https://boost-ext.github.io/ut/"
    license = "Boost"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    exports_sources = "include/*"
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        self.copy("*.hpp")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "UT"
        self.cpp_info.names["cmake_find_package_multi"] = "UT"
