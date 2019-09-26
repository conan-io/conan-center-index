#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            with tools.environment_append(RunEnvironment(self).vars):
                bin_path = os.path.join("bin", "test_package")
                arguments = "%sw+ Bincrafters" % ("\\" if self.settings.os == "Windows" else "\\\\")
                if self.settings.os == "Windows":
                    self.run("%s %s" % (bin_path, arguments))
                elif self.settings.os == "Macos":
                    self.run("DYLD_LIBRARY_PATH=%s %s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path, arguments))
                else:
                    self.run("LD_LIBRARY_PATH=%s %s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path, arguments))
