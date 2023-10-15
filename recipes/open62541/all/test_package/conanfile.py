from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("ua-nodeset/padim-1.02-2021-07-21")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["open62541_NODESET_DIR"] = self.dependencies["ua-nodeset"].conf_info.get(
            "user.ua-nodeset:nodeset_dir").replace("\\", "/")  # sanitize path for windows systems
        tc.variables["open62541_TOOLS_DIR"] = self.dependencies["open62541"].conf_info.get(
            "user.open62541:tools_dir")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
