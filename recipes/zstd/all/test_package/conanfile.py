from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.errors import ConanException
from io import StringIO
from conan.tools.files import load, save
import re
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

        zstd_version = load(self, os.path.join(self.generators_folder, "zstd_version"))

        output = StringIO()
        self.run(f"zstd --version", output, env="conanrun")
        output_str = str.strip(output.getvalue())

        s = re.search(f"{zstd_version}", output_str)
        if s == None:
            raise ConanException(f"zstd command output '{output_str}' should contain version string '{zstd_version}'")
        else:
            self.output.info(f"Version verified: '{zstd_version}'")
