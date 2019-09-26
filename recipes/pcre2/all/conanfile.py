#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class PCREConan(ConanFile):
    name = "pcre2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Perl Compatible Regular Expressions"
    topics = "regex", "regexp", "regular expressions", "PCRE"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bzip2": [True, False],
        "build_pcre2_8": [True, False],
        "build_pcre2_16": [True, False],
        "build_pcre2_32": [True, False],
        "support_jit": [True, False]
    }
    default_options = {'shared': False, 'fPIC': True, 'with_bzip2': True, 'build_pcre2_8': True,
                       'build_pcre2_16': True, 'build_pcre2_32': True, 'support_jit': True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    requires = "zlib/1.2.11"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_bzip2:
            self.requires.add("bzip2/1.0.8")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PCRE2_BUILD_TESTS"] = False
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            runtime = not self.options.shared and "MT" in self.settings.compiler.runtime
            cmake.definitions["PCRE2_STATIC_RUNTIME"] = runtime
        cmake.definitions["PCRE2_DEBUG"] = self.settings.build_type == "Debug"
        cmake.definitions["PCRE2_BUILD_PCRE2_8"] = self.options.build_pcre2_8
        cmake.definitions["PCRE2_BUILD_PCRE2_16"] = self.options.build_pcre2_16
        cmake.definitions["PCRE2_BUILD_PCRE2_32"] = self.options.build_pcre2_32
        cmake.definitions["PCRE2_SUPPORT_JIT"] = self.options.support_jit
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        cmake.patch_config_paths()
        tools.rmdir(os.path.join(self.package_folder, "man"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy(pattern="LICENCE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        def library_name(library):
            if self.settings.build_type == "Debug" and self.settings.os == "Windows":
                library += "d"
            if self.settings.compiler == "gcc" and self.settings.os == "Windows" and self.options.shared:
                library += ".dll"
            return library

        self.cpp_info.libs = [library_name("pcre2-posix")]
        if self.options.build_pcre2_8:
            self.cpp_info.libs.append(library_name("pcre2-8"))
        if self.options.build_pcre2_16:
            self.cpp_info.libs.append(library_name("pcre2-16"))
        if self.options.build_pcre2_32:
            self.cpp_info.libs.append(library_name("pcre2-32"))
        if not self.options.shared:
            self.cpp_info.defines.append("PCRE2_STATIC")