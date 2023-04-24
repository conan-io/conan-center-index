from conan import ConanFile, conan_version
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=can_run(self))

    def build_requirements(self):
        if not can_run(self):
            self.tool_requires(self.tested_reference_str)

    def generate(self):
        VirtualRunEnv(self).generate()
        if can_run(self):
            VirtualRunEnv(self).generate(scope="build")
        else:
            VirtualBuildEnv(self).generate()

    def build(self):
        calc_wsdl = os.path.join(self.source_folder, "calc.wsdl")
        self.output.info(f"Generating code from WSDL '{calc_wsdl}'")
        self.run(f"wsdl2h -o calc.h {calc_wsdl}")
        if Version(conan_version).major < "2":
            # conan v1 limitation: self.dependencies is not defined in build() method of test package
            import_dir = os.path.join(self.deps_cpp_info["gsoap"].rootpath, "bin", "import")
        else:
            import_dir = os.path.join(self.dependencies["gsoap"].package_folder, "bin", "import")
        self.run(f"soapcpp2 -j -CL -I{import_dir} calc.h")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
