from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(self.tested_reference_str)

    def build(self):
        with tools.no_op() if hasattr(self, "settings_build") else tools.run_environment(self):
            calc_wsdl = os.path.join(self.source_folder, os.pardir, "test_package", "calc.wsdl")
            self.output.info(f"Generating code from WSDL '{calc_wsdl}'")
            self.run(f"wsdl2h -o calc.h {calc_wsdl}")
            import_dir = os.path.join(self.deps_cpp_info["gsoap"].rootpath, "bin", "import")
            self.run(f"soapcpp2 -j -CL -I{import_dir} calc.h")

            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
