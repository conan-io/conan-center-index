import os

from conans import ConanFile, CMake, tools


class KcovTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake"]

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BUILD_TYPE"] = "Debug"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bindir = os.path.join("bin", "test_package")
            args = ["--exclude-pattern=/usr/",
                    "--include-path={}".format(self.source_folder),
                    "cov",
                    bindir]
            self.run("kcov {}".format(" ".join(args)), run_environment=True)
