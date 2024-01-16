from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def test(self):
        # FIXME: Can't actually run this since Ruby and required Ruby gems are not set up
        if self.settings.os == "Windows":
            self.run("where ign", run_environment=True)
        else:
            self.run("which ign", run_environment=True)
