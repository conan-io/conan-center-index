from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps
from conan.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        if can_run(self):
            tc = CMake(self)
            tc.configure()
            tc.build()

    def test(self):
        if can_run(self):
            if not os.path.isdir(os.path.join(self.build_folder, "html")):
                raise ConanException("doxygen did not create html documentation directory")
            self.output.info("Version:")
            self.run("doxygen --version", run_environment=True)

