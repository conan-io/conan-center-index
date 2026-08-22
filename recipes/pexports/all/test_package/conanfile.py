import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            self.run("pexports -H")

            if self.settings.os == "Windows":
                bin_path = os.path.join(self.cpp.build.bindir, "test_package")
                self.run(bin_path, env="conanrun")
                exports_def_path = os.path.join(self.build_folder, "exports.def")
                exports_def_contents = load(self, exports_def_path)
                self.output.info(f"{exports_def_path} contents:\n{exports_def_contents}")
                if "test_package_function" not in exports_def_contents:
                    raise ConanException("pexport could not detect `test_package_function` in the dll")
