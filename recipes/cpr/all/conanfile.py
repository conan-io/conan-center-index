#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class CprConan(ConanFile):
    name = "cpr"
    version = "1.3.0"
    url = "https://github.com/DEGoodmanWilson/conan-cpr"
    description = "Keep it short"
    license = "https://github.com/whoshuu/cpr/blob/1.3.0/LICENSE"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "use_ssl": [True, False]}
    default_options = "shared=False", "libcurl:with_ldap=False", "use_ssl=True"

    requires = "libcurl/7.56.1"
    generators = "cmake"

    def requirements(self):
        if self.options.use_ssl:
            self.options["libcurl"].with_openssl = True
        else:
            self.options["libcurl"].with_openssl = False

        if tools.os_info.is_macos:
            if "libcurl" in self.requires:
                del self.requires["libcurl"]


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["USE_SYSTEM_CURL"] = True # Force CPR to not try to build curl itself from a git submodule
        cmake.definitions["BUILD_CPR_TESTS"] = False
        cmake.configure()
        cmake.build()

    def package(self):
        with tools.chdir("sources"):
            self.copy(pattern="LICENSE")
            self.copy(pattern="*", dst="include", src="sources/include", keep_path=True)
            self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if tools.os_info.is_macos:
            self.cpp_info.libs.append("curl")