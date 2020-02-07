from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    _lib_suffix = {
        "Linux": "so",
        "Macos": "dylib",
        "Windows": "dll",
    }

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            libdir = "bin" if self.settings.os == "Windows" else "lib"
            lib_path = os.path.join(libdir, "liba.{}".format(self._lib_suffix[str(self.settings.os)]))
            self.run("{} {}".format(bin_path, lib_path), run_environment=True)
