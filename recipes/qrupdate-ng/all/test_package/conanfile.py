from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def _fortran_compiler(self):
        # Same lookup as the recipe: configured compiler, then gfortran in the system
        comp_exe = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        return comp_exe.get("fortran") or shutil.which("gfortran")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")
        if not self._fortran_compiler:
            # The library was built with the gcc package: its Fortran runtime is needed to link the test
            self.tool_requires("gcc/[>=11]")

    def generate(self):
        env = VirtualBuildEnv(self)
        if not self._fortran_compiler:
            # Use the gcc package only for its Fortran runtime: keep the C/C++ compilers of the profile.
            buildenv = env.environment()
            for var in ("CC", "CXX", "AR", "NM", "RANLIB"):
                buildenv.unset(var)
        env.generate()

        tc = CMakeToolchain(self)
        if not self._fortran_compiler:
            gcc_libdir = os.path.join(self.dependencies.build["gcc"].package_folder, "lib")
            tc.extra_exelinkflags.extend([f"-L{gcc_libdir}", f"-Wl,-rpath,{gcc_libdir}"])
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
