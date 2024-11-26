from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    @property
    def _nats_library_name(self):
        suffix = "" if self.dependencies["cnats"].options.shared else "_static"
        debug = "d" if self.dependencies["cnats"].settings.build_type == "Debug" else ""
        return f"nats{suffix}{debug}"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CNATS_TARGET"] = self._nats_library_name
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
