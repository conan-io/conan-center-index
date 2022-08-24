#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile, tools
from conans import CMake, RunEnvironment
from conan.tools.build import cross_building
import os
import subprocess
import re


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
