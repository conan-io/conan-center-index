from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package", "pkg_config"

    def build(self):
        pcfiles =  ["libbsd", "libbsd-overlay"]
        if self.settings.compiler != "apple-clang":
            pcfiles.append("libbsd-ctor")
        for f in pcfiles:
            pc = "{}.pc".format(f)
            if not os.path.isfile(pc):
                raise ConanException("{} not created by pkg_config generator".format(pc))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
