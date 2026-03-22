from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, chdir, replace_in_file
from conan.tools.scm import Git
from conan.tools.cmake import CMakeToolchain, CMake

import os

required_conan_version = ">=2"


class Dawn(ConanFile):
    name = "dawn"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Native WebGPU implementation"
    license = "BSD-3-Clause"
    homepage = "https://dawn.googlesource.com/dawn"
    topics = ("rendering", "graphics", "wgsl")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    def validate(self):
        if self.options.shared:
            raise ConanInvalidConfiguration(
                "Building as a shared library is not implemented yet"
            )

        if self.settings.os == "Emscripten":
            raise ConanInvalidConfiguration(
                "For the emscripten port of dawn, use https://github.com/conan-io/conan-toolchains/blob/main/recipes/emsdk/config.yml"
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        git = Git(self)
        git.clone(url=self.homepage, target=".")
        git.checkout(**self.conan_data["sources"][self.version])
        self.run("python tools/fetch_dawn_dependencies.py")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DAWN_ENABLE_INSTALL"] = "ON"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
