from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.env import VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    # FIXME: we should test btyacc as a build requirement and
    #        add btyacc to build_context_activated of CMakDeps but there is a
    #        conan client bug: https://github.com/conan-io/conan/issues/14758

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        if can_run(self):
            VirtualRunEnv(self).generate(scope="build")

    def build(self):
        if can_run(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type}", env="conanrun")
