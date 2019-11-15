from conans import ConanFile, CMake, tools
import os


class PackageTest(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            # Handle mingw
            if self.settings.os == "Windows":
                ext = ".exe"
            else:
                ext = ""
            assert(os.path.exists(os.path.join("bin", "example%s" % ext)))
        else:
            exec_path = os.path.join('bin', 'example')
            self.run(exec_path, run_environment=True)
