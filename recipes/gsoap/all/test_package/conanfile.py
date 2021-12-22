import os
from conans import ConanFile, CMake, tools

class TestGsoapConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        # TODO: Add some test for the cross-building scenario

        if not tools.cross_building(self):
            calc_wsdl = os.path.join(os.path.dirname(__file__), 'calc.wsdl')
            self.output.info("Generating code from WSDL '{}'".format(calc_wsdl))
            self.run("wsdl2h -o calc.h {}".format(calc_wsdl), run_environment=True)
            self.run("soapcpp2 -j -CL -I{} calc.h".format(os.path.join(self.deps_cpp_info["gsoap"].rootpath, 'bin', 'import')), run_environment=True)

            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "gsoap_example")
            self.run(bin_path, run_environment=True)
