from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _executables(self):
        all_execs = ("gl-info", "al-info", "distancefieldconverter", "fontconverter", "imageconverter", "sceneconverter")
        return [it for it in all_execs if getattr(self.options["magnum"], "with_{}".format(it.replace("-", "_")))]

    def build(self):
        cmake = CMake(self)
        for exec in self._executables:
            cmake.definitions["EXEC_{}".format(exec.replace("-", "_")).upper()] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            for exec in self._executables:
                self.run("magnum-{} --help".format(exec), run_environment=True)

            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
