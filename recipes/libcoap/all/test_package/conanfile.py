import os
from conan import ConanFile, tools
from conans import CMake


class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)

        version = self.deps_cpp_info["libcoap"].version;
        if version == "cci.20200424":
            cmake.definitions["LIB_VERSION"] = 2
        else:
            cmake.definitions["LIB_VERSION"] = 3

        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            bin_path = os.path.join("bin", "test_package")
            bin_path = self.run(bin_path, run_environment=True)
