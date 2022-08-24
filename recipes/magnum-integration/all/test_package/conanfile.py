import os
from conan import ConanFile, tools
from conans import CMake

class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_BULLET"] = self.options["magnum-integration"].with_bullet
        cmake.definitions["WITH_DART"] = self.options["magnum-integration"].with_dart
        cmake.definitions["WITH_EIGEN"] = self.options["magnum-integration"].with_eigen
        cmake.definitions["WITH_GLM"] = self.options["magnum-integration"].with_glm
        cmake.definitions["WITH_IMGUI"] = self.options["magnum-integration"].with_imgui
        cmake.definitions["WITH_OVR"] = self.options["magnum-integration"].with_ovr
        cmake.configure()
        cmake.build()


    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

        if self.settings.os == "Emscripten":
            bin_path = os.path.join("bin", "test_package.js")
            self.run("node {}".format(bin_path), run_environment=True)
