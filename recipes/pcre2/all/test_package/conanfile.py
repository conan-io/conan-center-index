#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        if self.settings.os == "Windows" and not self.options['pcre2'].shared:
            cmake.definitions['PCRE2_STATIC'] = True
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        arguments = "%sw+ Bincrafters" % ("\\" if self.settings.os == "Windows" else "\\\\")
        self.run("%s %s" % (bin_path, arguments), run_environment=True)