import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.build import cross_building
from conan.tools.scm import Version


class FooTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    # VirtualBuildEnv and VirtualRunEnv can be avoided if "tools.env.virtualenv:auto_use" is defined
    # (it will be defined in Conan 2.0)
    generators = "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"
    apply_env = False
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)
        tested_version = self.tested_reference_str.split('/')[1].split('@')[0]
        # using armadillo > 12.x requires the consumer to explicitly depend on hdf5
        if Version(tested_version) > "12":
            self.requires("hdf5/1.14.0")

    def generate(self):
        tc = CMakeToolchain(self)
        # using armadillo > 12.x requires explicit consumer linkage against hdf5
        explicit_link_condition = Version(self.dependencies["armadillo"].ref.version) > "12"
        tc.variables["LINK_HDF5"] = explicit_link_condition
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if not cross_building(self):
            cmd = os.path.join(self.cpp.build.bindirs[0], "example")
            self.run(cmd, env="conanrun")
