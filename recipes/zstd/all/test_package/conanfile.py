from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from io import StringIO
from conan.tools.files import load, save
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        zstd_version = self.dependencies["zstd"].ref.version
        save(self, "zstd_version", f"{zstd_version}")


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return

        bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
        png_file = os.path.join(self.source_folder, "logo.png")
        self.run(f"{bin_path} {png_file}", env="conanrun")

        zstd_version = load(self, os.path.join(self.generators_folder, "zstd_version"))

        output = StringIO()
        self.run(f"zstd --version", output, env="conanrun")
        output_str = str.strip(output.getvalue())
        assert zstd_version in output_str, f"zstd command output '{output_str}' should contain version string '{zstd_version}'"
        self.output.info(f"Version verified: '{zstd_version}'")
