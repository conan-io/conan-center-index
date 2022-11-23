from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        # TODO: Add some test for the cross-building scenario

        if not tools.cross_building(self):
            calc_wsdl = os.path.join(self.source_folder, os.pardir, "test_package", "calc.wsdl")
            self.output.info(f"Generating code from WSDL '{calc_wsdl}'")
            self.run(f"wsdl2h -o calc.h {calc_wsdl}", run_environment=True)
            import_dir = os.path.join(self.deps_cpp_info["gsoap"].rootpath, "bin", "import")
            self.run(f"soapcpp2 -j -CL -I{import_dir} calc.h", run_environment=True)

            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
