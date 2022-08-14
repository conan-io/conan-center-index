from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.gnu import Autotools
from conans import tools as tools_legacy
import os
import shutil


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
        if self._settings_build.os == "Windows" and not tools_legacy.get_env("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        if self.options["pkgconf"].enable_lib:
            tc = CMakeToolchain(self)
            tc.generate()
            cd = CMakeDeps(self)
            cd.generate()

    def build(self):
        shutil.copy(os.path.join(self.source_folder, "configure.ac"),
                    os.path.join(self.build_folder, "configure.ac"))
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()

        if self.options["pkgconf"].enable_lib:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not cross_building(self):
            if self.options["pkgconf"].enable_lib:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
                self.run(bin_path, env="conanrun")

            pkg_config = tools_legacy.get_env("PKG_CONFIG")
            self.output.info("Read environment variable PKG_CONFIG='{}'".format(pkg_config))
            if not pkg_config or not pkg_config.startswith(self.deps_cpp_info["pkgconf"].rootpath.replace("\\", "/")):
                raise ConanException("PKG_CONFIG variable incorrect")

            pkgconf_path = tools_legacy.which("pkgconf").replace("\\", "/")
            self.output.info("Found pkgconf at '{}'".format(pkgconf_path))
            if not pkgconf_path or not pkgconf_path.startswith(self.deps_cpp_info["pkgconf"].rootpath.replace("\\", "/")):
                raise ConanException("pkgconf executable not found")

            with tools_legacy.environment_append({"PKG_CONFIG_PATH": self.source_folder}):
                self.run("{} libexample1 --libs".format(os.environ["PKG_CONFIG"]), env="conanbuild")
                self.run("{} libexample1 --cflags".format(os.environ["PKG_CONFIG"]), env="conanbuild")
