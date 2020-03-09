#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from conans import ConanFile, CMake, tools


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        assert os.path.exists(os.path.join(self.deps_cpp_info["zlib"].rootpath, "licenses", "LICENSE"))
        if "x86" in self.settings.arch and not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
