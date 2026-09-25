from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import can_run

import os


class CppMicroServicesTestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"

    @property
    def _has_compendium(self):
        opts = self.dependencies[self.tested_reference_str].options
        return bool(opts.shared and opts.with_threading)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        # This tool_requires() is used to exercise the usResourceCompiler and SCRCodeGen tools
        # within the build context of a downstream consumer of the CppMicroServices recipe. These
        # tools are required during the build process of bundles. If these tools were unavailable to
        # downstream consumers, while they would be able to link against CppMicroServices and use
        # the framework, they wouldn't be able to author their own bundles.
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["US_HAS_COMPENDIUM"] = self._has_compendium
        if self._has_compendium:
            dep = self.dependencies[self.tested_reference_str]
            if self.settings.os == "Windows":
                pkg_bundle_dir = dep.cpp_info.bindir
            else:
                pkg_bundle_dir = dep.cpp_info.libdir
            tc.variables["US_PACKAGE_BUNDLE_DIR"] = pkg_bundle_dir.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.build_folder, "bin", "test_package")
            self.run(f"{bin_path}", env="conanrun")
