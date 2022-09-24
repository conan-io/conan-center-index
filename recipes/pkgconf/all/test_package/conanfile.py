from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
from conan.tools.gnu import Autotools
from conans import tools as tools_legacy
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "AutotoolsToolchain", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("automake/1.16.5")
        if self._settings_build.os == "Windows" and \
           not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        if self.dependencies["pkgconf"].options.enable_lib:
            tc = CMakeToolchain(self)
            tc.generate()
            cd = CMakeDeps(self)
            cd.generate()

    def build(self):
        copy(self, "libexample1.pc", src=self.source_folder, dst=self.generators_folder)
        autotools = Autotools(self)
        self.win_bash = True
        autotools.autoreconf()
        autotools.configure()
        self.win_bash = False

        if self.options["pkgconf"].enable_lib:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self) and self.options["pkgconf"].enable_lib:
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

        pkg_config = tools_legacy.get_env("PKG_CONFIG")
        self.run(f"{pkg_config} libexample1 --libs")
        self.run(f"{pkg_config} libexample1 --cflags")
