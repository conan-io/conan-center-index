from conan import ConanFile, conan_version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class NinjaConan(ConanFile):
    name = "ninja"
    package_type = "application"
    description = "Ninja is a small build system with a focus on speed"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ninja-build/ninja"
    topics = ("ninja", "build")
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        if self.settings.os == "Linux" and "libstdc++" in self.settings.compiler.libcxx:
            # Link C++ library statically on Linux so that it can run on systems
            # with an older C++ runtime
            tc.cache_variables["CMAKE_EXE_LINKER_FLAGS"] = "-static-libstdc++ -static-libgcc"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2
        if Version(conan_version).major < 2:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
            self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
