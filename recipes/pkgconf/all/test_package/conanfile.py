from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfig
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    enable_lib = False

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if is_msvc(self):
            self.tool_requires("automake/1.16.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        virtual_run_env = VirtualRunEnv(self)
        virtual_run_env.generate()
        autotools_toolchain = AutotoolsToolchain(self)
        autotools_toolchain.generate()
        if self.dependencies.direct_host["pkgconf"].options.enable_lib:
            self.enable_lib = True
            cmake_toolchain = CMakeToolchain(self)
            cmake_toolchain.generate()
            cmake_deps = CMakeDeps(self)
            cmake_deps.generate()

    def build(self):
        # Test pkg.m4 integration into automake
        copy(self, "configure.ac", self.source_folder, self.build_folder)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()

        if self.enable_lib:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            if self.enable_lib:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
                self.run(bin_path, env="conanrun")

            pkgconf_path = self.conf.get("tools.gnu:pkg_config", default=False, check_type=str)
            if pkgconf_path:
                self.output.info(f"Found pkgconf at '{pkgconf_path}'")
            else:
                raise ConanException("pkgconf executable not found")

            pkg_conf = PkgConfig(self, "libexample1", pkg_config_path=self.source_folder)
            self.output.info(f"libexample1 libs: {pkg_conf.libs}")
            self.output.info(f"libexample1 cflags: {pkg_conf.cflags}")
