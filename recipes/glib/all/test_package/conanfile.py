from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.gnu import PkgConfig, PkgConfigDeps
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self.settings.os != "Windows" and not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        virtual_run_env = VirtualRunEnv(self)
        virtual_run_env.generate()

        if self.settings.os == "Macos":
            env = Environment()
            # Avoid conflicts with system libiconv
            # see: https://github.com/conan-io/conan-center-index/pull/17610#issuecomment-1552921286
            env.define_path("DYLD_FALLBACK_LIBRARY_PATH", "$DYLD_LIBRARY_PATH")
            env.define_path("DYLD_LIBRARY_PATH", "")
            env.vars(self, scope="run").save_script("conanrun_macos_runtimepath")

        if self.settings.os == "Windows":
            deps = CMakeDeps(self)
            deps.generate()
        else:
            virtual_build_env = VirtualBuildEnv(self)
            virtual_build_env.generate()
            pkg_config_deps = PkgConfigDeps(self)
            pkg_config_deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

            if self.settings.os != "Windows":
                pkg_config = PkgConfig(self, "gio-2.0", pkg_config_path=self.generators_folder)
                gdbus_codegen = pkg_config.variables["gdbus_codegen"]
                self.run(f"{gdbus_codegen} -h", env="conanrun")
