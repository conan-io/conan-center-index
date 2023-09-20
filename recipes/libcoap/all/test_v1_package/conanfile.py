import os
from conans import ConanFile, CMake, tools


class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        version = self.deps_cpp_info["libcoap"].version
        lib_version = 2 if version == "cci.20200424" else 3
        cmake.definitions["CMAKE_CXX_FLAGS"] = f"-DLIB_VERSION={lib_version}"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
