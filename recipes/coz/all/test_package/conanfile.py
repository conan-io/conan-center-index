import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if self.settings.build_type not in ["Debug", "RelWithDebInfo"]:
            self.output.info(f"Skipping coz test because {self.settings.build_type} "
                             "build type does not contain debug information")
            return
        if self.settings.os == "Linux":
            perf_even_paranoid = int(open("/proc/sys/kernel/perf_event_paranoid").read())
            is_root = os.geteuid() == 0
            if perf_even_paranoid > 2 and not is_root:
                self.output.info("Skipping coz test because /proc/sys/kernel/perf_event_paranoid value "
                                 f"must be <= 2 (currently {perf_even_paranoid}) and not running as root")
                return
        if can_run(self):
            with chdir(self, self.cpp.build.bindir):
                self.run("coz run --- ./test_package", env="conanrun")
                print(open("profile.coz").read())
