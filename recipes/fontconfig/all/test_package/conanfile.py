#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from conans import ConanFile, CMake, tools, RunEnvironment


class FontconfigTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "example")
        env = {"FONTCONFIG_PATH": os.path.join(self.deps_cpp_info["fontconfig"].rootpath, "etc", "fonts")}
        with tools.environment_append(env):
            self.run(bin_path, run_environment=True)
