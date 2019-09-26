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
        if tools.cross_building(self.settings):
            return
        img_name = os.path.join(self.source_folder, "testimg.jpg")
        bin_path = os.path.join("bin", "test_package")
        command = "%s %s" % (bin_path, img_name)
        self.run(command, run_environment=True)
