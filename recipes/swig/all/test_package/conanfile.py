from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import cross_building
from conan.tools.microsoft import is_msvc

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    @property
    def _can_build(self):
        # FIXME: Python does not distribute debug libraries (use cci CPython recipe)
        return not (is_msvc(self) and self.settings.build_type == "Debug")

    def requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        if not cross_building(self, skip_x64_x86=True):
            self.run("swig -swiglib", env="conanbuild")
            if self._can_build:
                cmake = CMake(self)
                cmake.verbose = True
                cmake.configure()
                cmake.build()

    def test(self):
        if not cross_building(self):
            if self._can_build:
                cmake = CMake(self)
                cmake.test()
            self.run("swig -version", env="conanbuild")
