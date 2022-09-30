from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, cmake_layout
import os

class TestGsoapConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        # TODO: Add some test for the cross-building scenario

        if not cross_building(self):
            calc_wsdl = os.path.join(self.source_folder, "calc.wsdl")
            self.output.info("Generating code from WSDL '{}'".format(calc_wsdl))
            self.run("wsdl2h -o calc.h {}".format(calc_wsdl), run_environment=True)
            self.run("soapcpp2 -j -CL -I{} calc.h".format(os.path.join(self.deps_cpp_info["gsoap"].rootpath, 'bin', 'import')), run_environment=True)

            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
