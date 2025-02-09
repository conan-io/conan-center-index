import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=can_run(self))

    def build_requirements(self):
        if not can_run(self):
            self.tool_requires(self.tested_reference_str)
            self.tool_requires("cmake/[>=3.27 <4]")

    def generate(self):
        path = self.dependencies["qt"].package_folder.replace("\\", "/")
        save(self, "qt.conf", f"[Paths]\nPrefix = {path}\n")

    @property
    def _can_build(self):
        if can_run(self):
            qt = self.dependencies["qt"]
        else:
            qt = self.dependencies.build["qt"]
        return qt.options.gui and qt.options.widgets

    def build(self):
        if self._can_build:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            self.run("moc --version")
            if self._can_build:
                copy(self, "qt.conf", self.generators_folder, self.cpp.build.bindir)
                bin_path = os.path.join(self.cpp.build.bindir, "test_package")
                self.run(bin_path, env="conanrun")
                # Related to https://github.com/conan-io/conan-center-index/issues/20574
                if self.settings.os == "Macos":
                    bin_macos_path = os.path.join(self.cpp.build.bindir, "test_macos_bundle.app", "Contents", "MacOS", "test_macos_bundle")
                    self.run(bin_macos_path, env="conanrun")
