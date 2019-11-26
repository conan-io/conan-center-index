#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from conans import ConanFile, CMake, tools


class TestKDSoapConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        assert os.path.exists(os.path.join(self.deps_cpp_info["kdsoap"].rootpath, "licenses", "LICENSE.txt"))
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "kdsoap_test")
            self.run(bin_path, run_environment=True)

