#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, CMake
import os


license = """================================================================================
OpenGL Mathematics (GLM)
--------------------------------------------------------------------------------
GLM is licensed under The Happy Bunny License and MIT License

================================================================================
The Happy Bunny License (Modified MIT License)
--------------------------------------------------------------------------------
Copyright (c) 2005 - 2014 G-Truc Creation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

Restrictions:
 By making use of the Software for military purposes, you choose to make a
 Bunny unhappy.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

================================================================================
The MIT License
--------------------------------------------------------------------------------
Copyright (c) 2005 - 2014 G-Truc Creation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""


class GlmConan(ConanFile):
    name = "glm"
    version = "0.9.9.5"
    description = "OpenGL Mathematics (GLM)"
    topics = ("conan", "glm", "opengl", "mathematics")
    url = "https://github.com/bincrafters/conan-glm"
    homepage = "https://github.com/g-truc/glm"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    generators = "cmake"
    no_copy_source = True

    exports = ["LICENSE.md"]
    exports_sources = [
        "CMakeLists.txt",
        "0001-Remove-architecture-check-from-CMake-package.patch"
    ]

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "glm-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["GLM_TEST_ENABLE"] = False
        cmake.definitions["BUILD_SHARED_LIBS"] = False
        cmake.definitions["BUILD_STATIC_LIBS"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        with tools.chdir(self.source_folder):
            tools.patch(base_path=self._source_subfolder, patch_file="0001-Remove-architecture-check-from-CMake-package.patch")
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        os.makedirs(os.path.join(self.package_folder, "licenses"))
        tools.save(os.path.join(self.package_folder, "licenses", "COPYING.txt"), license)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_id(self):
        self.info.header_only()
