from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.build import can_run
from conans.errors import ConanException

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def test(self):
        if can_run(self):
            # INFO: The --help option does not cause a 0 exit code as usual
            # INFO: The exit code is different between 32 and 64 bits due to overflow
            retcode_expected = 2676788828 if self.settings.arch == "x86_64" else -1618178468
            retcode_received = self.run("OpenCppCoverage.exe --help", env="conanrun", ignore_errors=True)

            if retcode_received != retcode_expected:
                raise ConanException(f"Error {retcode_received} while executing")
