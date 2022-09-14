from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake


class TkTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(str(self.build_path.joinpath("test_package")), run_environment=True, env="conanrun")
