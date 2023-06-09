from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["LIBMEDIAINFO_SHARED"] = self.options["libmediainfo"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            testsrc = os.path.join(self.source_folder, os.pardir, "test_package", "testsrc.mp4")
            self.run(f"{bin_path} {testsrc}", run_environment=True)
