import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import save, load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TILEDB_CPP_API"] = self.dependencies["tiledb"].options.cpp_api
        tc.generate()
        save(self, os.path.join(self.build_folder, "have_tools"), str(self.dependencies["tiledb"].options.tools))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package_cpp")
            if os.path.exists(bin_path):
                self.run(bin_path, env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindir, "test_package_c")
            self.run(bin_path, env="conanrun")

            have_tools = load(self, os.path.join(self.build_folder, "have_tools")) == "True"
            if have_tools:
                self.run("tiledb help info", env="conanrun")
