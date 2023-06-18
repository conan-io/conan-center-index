from conans import ConanFile, CMake, tools


class TestPackageV1Conan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("patchelf --version", run_environment=True)
