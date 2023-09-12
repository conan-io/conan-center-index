import os

from conan import ConanFile, conan_version
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.gnu import PkgConfig


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "PkgConfigDeps", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GLIB_INTROSPECTION_DATA_AVAILABLE"] = self.dependencies["glib"].options.shared
        tc.generate()

    def build(self):
        if self.settings.os != "Windows":
            if conan_version >= "2":
                # Conan v1 has a bug and fails with 'Variable 'libdir' not defined in gobject-introspection-1.0.pc'
                pkg_config = PkgConfig(self, "gobject-introspection-1.0", pkg_config_path=self.generators_folder)
                for tool in ["g_ir_compiler", "g_ir_generate", "g_ir_scanner"]:
                    self.run("%s --version" % pkg_config.variables[tool], env="conanrun")
            self.run("g-ir-annotation-tool --version", env="conanrun")
            self.run("g-ir-inspect -h", env="conanrun")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        bin_path = os.path.join(self.cpp.build.bindir, "test_basic")
        self.run(bin_path, env="conanrun")

        bin_path = os.path.join(self.cpp.build.bindir, "test_girepository")
        if os.path.exists(bin_path):
            self.run(bin_path, env="conanrun")
