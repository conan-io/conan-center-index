from conans import ConanFile, CMake, tools, RunEnvironment
import os
import shutil
from conans.tools import Version


class TestPackageConan(ConanFile):
    settings = "cppstd", "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

            self.run("thrift --version", run_environment=True)


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _thrift_compiler_available(self):
        return not tools.cross_building(self.settings)

    def build(self):
        # Build without thrift compiler
        shutil.copytree(os.path.join(self.source_folder,
                                     self.deps_cpp_info["thrift"].version), "without_thrift_compiler")

        thrift_version = Version(self.deps_cpp_info["thrift"].version)
        # C++11 is mandatory in 0.13.0. Before 0.13.0, use Boost as C++11 is not supported
        use_cxx_11 = int(
            thrift_version.minor) >= 13 and tools.valid_min_cppstd(self, "11")

        cmake = CMake(self)
        cmake.definitions["THRIFT_COMPILER_AVAILABLE"] = False
        cmake.definitions["USE_CXX_11"] = use_cxx_11
        cmake.configure(build_folder="without_thrift_compiler")
        cmake.build()

        with tools.environment_append(RunEnvironment(self).vars):
            if self._thrift_compiler_available:
                # Build with protoc
                cmake = CMake(self)
                cmake.definitions["THRIFT_COMPILER_AVAILABLE"] = True
                cmake.definitions["USE_CXX_11"] = use_cxx_11
                cmake.configure(build_folder="with_thrift_compiler")
                cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("thrift --version", run_environment=True)

            # Test the build built without thrift compiler
            bin_path = os.path.join(
                "without_thrift_compiler", "bin", "test_package")
            self.run(bin_path, run_environment=True)

            if self._thrift_compiler_available:
                # Test the build built with thrift compiler
                assert os.path.isfile(os.path.join(
                    "with_thrift_compiler", "Calculator.cpp"))
                assert os.path.isfile(os.path.join(
                    "with_thrift_compiler", "Calculator.h"))
                bin_path = os.path.join(
                    "with_thrift_compiler", "bin", "test_package")
                self.run(bin_path, run_environment=True)
