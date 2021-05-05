#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        is_at_least_cpp11 = None
        try: 
            tools.check_min_cppstd(self, "11")
            is_at_least_cpp11 = True
        except Exception as error :
            is_at_least_cpp11 = False
        bin_path = os.path.join("bin", "test_package")
        if self.settings.os == "Windows" and is_at_least_cpp11:
            self.run(bin_path)
        elif self.settings.os == "Macos" and is_at_least_cpp11:
            self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path))
        elif is_at_least_cpp11:
            self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path))
        else:
            pass 
