#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, tools


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    version = "2.0.2"
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    topics = ("conan", "jpeg", "libjpeg", "image", "multimedia", "format", "graphics")
    url = "http://github.com/bincrafters/conan-libjpeg-turbo"
    author = "Bincrafters <bincrafters@gmail.com>"
    homepage = "https://libjpeg-turbo.org"
    license = "BSD-3-Clause, Zlib"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "SIMD": [True, False],
               "arithmetic_encoder": [True, False],
               "arithmetic_decoder": [True, False],
               "libjpeg7_compatibility": [True, False],
               "libjpeg8_compatibility": [True, False],
               "mem_src_dst": [True, False],
               "turbojpeg": [True, False],
               "java": [True, False],
               "enable12bit": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True,
                       'SIMD': True,
                       'arithmetic_encoder': True,
                       'arithmetic_decoder': True,
                       'libjpeg7_compatibility': True,
                       'libjpeg8_compatibility': True,
                       'mem_src_dst': True,
                       'turbojpeg': True,
                       'java': False,
                       'enable12bit': False}
    _source_subfolder = "source_subfolder"

    def build_requirements(self):
        self.build_requires("nasm/2.14")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")
        if self.settings.os == "Emscripten":
            del self.options.SIMD

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libjpeg-turbo-%s" % self.version, self._source_subfolder)
        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                  os.path.join(self._source_subfolder, "CMakeLists_original.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

    @property
    def _simd(self):
        if self.settings.os == "Emscripten":
            return False
        return self.options.SIMD

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions['ENABLE_STATIC'] = not self.options.shared
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['WITH_SIMD'] = self._simd
        cmake.definitions['WITH_ARITH_ENC'] = self.options.arithmetic_encoder
        cmake.definitions['WITH_ARITH_DEC'] = self.options.arithmetic_decoder
        cmake.definitions['WITH_JPEG7'] = self.options.libjpeg7_compatibility
        cmake.definitions['WITH_JPEG8'] = self.options.libjpeg8_compatibility
        cmake.definitions['WITH_MEM_SRCDST'] = self.options.mem_src_dst
        cmake.definitions['WITH_TURBOJPEG'] = self.options.turbojpeg
        cmake.definitions['WITH_JAVA'] = self.options.java
        cmake.definitions['WITH_12BIT'] = self.options.enable12bit
        cmake.configure(source_dir=self._source_subfolder)
        return cmake

    def build(self):
        # use standard GNUInstallDirs.cmake - custom one is broken
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists_original.txt"),
                              "include(cmakescripts/GNUInstallDirs.cmake)",
                              "include(GNUInstallDirs)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'doc'))

        # remove binaries
        for bin_program in ['cjpeg', 'djpeg', 'jpegtran', 'tjbench', 'wrjpgcom', 'rdjpgcom']:
            for ext in ['', '.exe']:
                try:
                    os.remove(os.path.join(self.package_folder, 'bin', bin_program+ext))
                except OSError:
                    pass

        self.copy("license*", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        # Copying generated header
        if self.settings.compiler == "Visual Studio":
            self.copy("jconfig.h", dst="include", src=".")

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.cpp_info.libs = ['jpeg', 'turbojpeg']
            else:
                self.cpp_info.libs = ['jpeg-static', 'turbojpeg-static']
        else:
            self.cpp_info.libs = ['jpeg', 'turbojpeg']
