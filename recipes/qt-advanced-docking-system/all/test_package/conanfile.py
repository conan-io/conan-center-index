from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("qt/[*]")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        ads = self.dependencies["qt-advanced-docking-system"]
        tc.variables["ADS_CMAKE_FILE_NAME"] = ads.cpp_info.get_property("cmake_file_name")
        tc.variables["ADS_CMAKE_TARGET_NAME"] = ads.cpp_info.get_property("cmake_target_name")
        version = Version(ads.ref.version)
        if version >= "5.1.0":
            tc.preprocessor_definitions["EXPECTED_ADS_VERSION"] = (
                (int(str(version.major)) << 16) | (int(str(version.minor)) << 8) | int(str(version.patch))
            )
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "example")
            self.run(bin_path, env="conanrun")
