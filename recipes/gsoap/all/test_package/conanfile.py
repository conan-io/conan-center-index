from conan import ConanFile
from conan.tools.build import can_run, cross_building
from conan.tools.cmake import CMake, cmake_layout
import os


class TestGsoapConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        # TODO: Add some test for the cross-building scenario

        if not cross_building(self):
            calc_wsdl = os.path.join(self.source_folder, "calc.wsdl")
            self.output.info(f"Generating code from WSDL '{calc_wsdl}'")
            self.run(f"wsdl2h -o calc.h {calc_wsdl}", env="conanrun")
            import_dir = os.path.join(self.deps_cpp_info["gsoap"].rootpath, "bin", "import")
            self.run(f"soapcpp2 -j -CL -I{import_dir} calc.h", env="conanrun")

            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
