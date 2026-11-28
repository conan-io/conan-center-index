from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class LlCppTestConan(ConanFile):
    test_type = "explicit"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not self.conf.get("user.package:in_local_cache", default=False):
            self.run("./ll-cpp-test", env="conanrun")
