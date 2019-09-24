#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanException


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.37"
    description = "libpng is the official PNG file format reference library."
    url = "http://github.com/bincrafters/conan-libpng"
    author = "Bincrafters <bincrafters@gmail.com>"
    homepage = "http://www.libpng.org"
    license = "libpng-2.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "api_prefix": "ANY"}
    default_options = {'shared': False, 'fPIC': True, "api_prefix": None}

    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires.add("zlib/1.2.11")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libpng-" + self.version, self._source_subfolder)

    def _patch(self):
        tools.patch(base_path=self._source_subfolder, patch_file=os.path.join("patches", "CMakeLists-zlib.patch"))
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "find_library(M_LIBRARY m)",
                              "set(M_LIBRARY m)")

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                     'OUTPUT_NAME "${PNG_LIB_NAME}_static',
                                     'OUTPUT_NAME "${PNG_LIB_NAME}')
            else:
                tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                      'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}',
                                      'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/$<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}')

        if self.settings.build_type == 'Debug':
            tools.replace_in_file(os.path.join(self._source_subfolder, 'libpng.pc.in'),
                                  '-lpng@PNGLIB_MAJOR@@PNGLIB_MINOR@',
                                  '-lpng@PNGLIB_MAJOR@@PNGLIB_MINOR@d')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.options.shared
        cmake.definitions["PNG_STATIC"] = not self.options.shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"
        if self.settings.os == "Emscripten":
            cmake.definitions["PNG_BUILD_ZLIB"] = "ON"
            cmake.definitions["M_LIBRARY"] = ""
            cmake.definitions["ZLIB_LIBRARY"] = self.deps_cpp_info["zlib"].libs[0]
            cmake.definitions["ZLIB_INCLUDE_DIR"] = self.deps_cpp_info["zlib"].include_paths[0]
        if self.options.api_prefix:
            cmake.definitions["PNG_PREFIX"] = self.options.api_prefix
        cmake.configure()
        return cmake

    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'libpng'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                self.cpp_info.libs = ["png"]
            else:
                self.cpp_info.libs = ['libpng16']
        else:
            self.cpp_info.libs = ["png16"]
            if self.settings.os == "Linux" or self.settings.os == "Android":
                self.cpp_info.libs.append("m")
        # use 'd' suffix everywhere except mingw
        if self.settings.build_type == "Debug" and not (self.settings.os == "Windows" and self.settings.compiler == "gcc"):
            self.cpp_info.libs[0] += "d"
