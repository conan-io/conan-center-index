from conan import ConanFile, tools
from conans import CMake
import os

# testsrc.mp4 generated with:
# ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 -c:v libx265 testsrc.mp4


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["LIBMEDIAINFO_SHARED"] = self.options["libmediainfo"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            testsrc = os.path.join(self.source_folder, "testsrc.mp4")
            self.run("{} {}".format(bin_path, testsrc), run_environment=True)
