import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        fastdds_version = self.conf.get("user.fast-dds-gen:fastdds_version", default="3.2.1")
        self.requires(f"fast-dds/{fastdds_version}")

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def build(self):
        self.run("fastddsgen -version")

        copy(self, "test.idl", src=self.source_folder, dst=self.build_folder)
        self.run("fastddsgen -replace test.idl", cwd=self.build_folder)

        expected_files = [
            "test.hpp",
            "testPubSubTypes.cxx",
            "testPubSubTypes.hpp",
            "testTypeObjectSupport.cxx",
            "testTypeObjectSupport.hpp",
        ]
        for expected_file in expected_files:
            filepath = os.path.join(self.build_folder, expected_file)
            if not os.path.exists(filepath):
                raise Exception(f"Expected generated file {expected_file} not found")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_generated")
            self.run(bin_path, env="conanrun")
