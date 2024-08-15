from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import mkdir, save, load
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        save(self, os.path.join(self.generators_folder, "bindir"),
             os.path.join(self.dependencies["crashpad"].package_folder, "bin"))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            test_env_dir = "test_env"
            mkdir(self, test_env_dir)
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            bindir = load(self, os.path.join(self.generators_folder, "bindir"))
            handler_exe = "crashpad_handler" + (".exe" if self.settings.os == "Windows" else "")
            handler_bin_path = os.path.join(bindir, handler_exe)
            self.run(f"{bin_path} {test_env_dir}/db {handler_bin_path}", env="conanrun")
            if self.settings.os == "Windows":
                handler_bin_path = os.path.join(bindir, "crashpad_handler.com")
                self.run(f"{bin_path} {test_env_dir}/db {handler_bin_path}", env="conanrun")
