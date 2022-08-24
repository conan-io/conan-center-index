from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        self.requires("ua-nodeset/padim-1.02-2021-07-21")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["open62541_NODESET_DIR"] = self.deps_user_info["ua-nodeset"].nodeset_dir
        cmake.definitions["open62541_TOOLS_DIR"] = self.deps_user_info["open62541"].tools_dir
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            # bin_path = os.path.join("bin", "test_package")
            # self.run(bin_path, run_environment=True)

            bin_path = os.path.join("bin", "test_package_nodeset")
            self.run(bin_path, run_environment=True)
