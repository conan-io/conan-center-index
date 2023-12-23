import os

from conan import ConanFile, conan_version
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.env import VirtualRunEnv
from conan.tools.files import mkdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    @property
    def _macos_workaround(self):
        return conan_version.major == 1 and self.options["flatcc"].shared and is_apple_os(self)

    def generate(self):
        VirtualRunEnv(self).generate(scope="build")
        VirtualRunEnv(self).generate(scope="run")
        tc = CMakeToolchain(self)
        tc.variables["MACOS_SIP_WORKAROUND"] = self._macos_workaround
        tc.generate()


    def build(self):
        cmake = CMake(self)
        if  self._macos_workaround:
            # Because of MacOS System Integrity Protection it is currently not possible to run the flatcc
            # executable from cmake if it is linked shared. As a temporary work-around run flatcc here in
            # the build function.
            gen_dir = os.path.join(self.build_folder, "generated")
            mkdir(self, gen_dir)
            fbs_file = os.path.join(self.source_folder, os.pardir, "test_package", "monster.fbs")
            self.run(f"flatcc -a -o {gen_dir} {fbs_file}")
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run("flatcc --version")
            bin_path = os.path.join(self.cpp.build.bindir, "monster")
            self.run(bin_path, env="conanrun")
