from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["QT_VERSION_MAJOR"] = tools.Version(self.deps_cpp_info["qt"].version).major
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            zipFile_path = os.path.join(self.source_folder, "zipFile.zip")
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path + " " + zipFile_path, run_environment=True)
