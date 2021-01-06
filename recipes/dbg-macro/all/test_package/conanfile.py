import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, minimal_cpp_standard)

        if tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                "dbg-mcro can't be used by {0} {1}".format(
                    self.settings.compiler,
                    self.settings.compiler.version
                )
            )

    def test(self):
        if not tools.cross_building(self.settings):
            tools.mkdir("logs/")
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
