from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    # TODO: Only keep logic under if hasattr(self, "settings_build") after conan v2.
    #       Indeed, v1 pipeline of c3i uses 1 profile, which can't work with
    #       build_context_activated & build_context_build_modules of CMakeDeps

    def requirements(self):
        if not hasattr(self, "settings_build"):
            self.requires(self.tested_reference_str)

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.tool_requires(self.tested_reference_str)

    def generate(self):
        if hasattr(self, "settings_build"):
            VirtualBuildEnv(self).generate()
            deps = CMakeDeps(self)
            deps.build_context_activated = ["btyacc"]
            deps.build_context_build_modules = ["btyacc"]
            deps.generate()
        else:
            if can_run(self):
                VirtualRunEnv(self).generate(scope="build")
                deps = CMakeDeps(self)
                deps.generate()

    def build(self):
        if hasattr(self, "settings_build") or can_run(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type}", env="conanrun")
