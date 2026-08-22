from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.dependencies["ouster_sdk"].options.build_osf:
            tc.preprocessor_definitions["WITH_OSF"] = "1"
        if self.dependencies["ouster_sdk"].options.build_pcap:
            tc.preprocessor_definitions["WITH_PCAP"] = "1"
        if self.dependencies["ouster_sdk"].options.build_viz:
            tc.preprocessor_definitions["WITH_VIZ"] = "1"
        if Version(self.dependencies["ouster_sdk"].ref.version) >= "0.15.0":
            if self.dependencies["ouster_sdk"].options.build_sensor:
                tc.preprocessor_definitions["WITH_SENSOR"] = "1"
            if self.dependencies["ouster_sdk"].options.build_mapping:
                tc.preprocessor_definitions["WITH_MAPPING"] = "1"
        tc.cache_variables["OUSTER_SDK_SHARED"] = self.dependencies["ouster_sdk"].options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
