# pylint: skip-file
from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools, RunEnvironment
from conans.errors import ConanException
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        self.build_requires("automake/1.16.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def build(self):
        # Test pkg.m4 integration into automake
        shutil.copy(os.path.join(self.source_folder, os.pardir, "test_package", "configure.ac"),
                    os.path.join(self.build_folder, "configure.ac"))
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.environment_append(RunEnvironment(self).vars):
            autotools.configure()

        if self.options["pkgconf"].enable_lib:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            if self.options["pkgconf"].enable_lib:
                self.run(os.path.join("bin", "test_package"), run_environment=True)

            pkg_config = tools.get_env("PKG_CONFIG")
            self.output.info("Read environment variable PKG_CONFIG='{}'".format(pkg_config))
            if not pkg_config or not pkg_config.startswith(self.deps_cpp_info["pkgconf"].rootpath.replace("\\", "/")):
                raise ConanException("PKG_CONFIG variable incorrect")

            pkgconf_path = tools.which("pkgconf").replace("\\", "/")
            self.output.info("Found pkgconf at '{}'".format(pkgconf_path))
            if not pkgconf_path or not pkgconf_path.startswith(self.deps_cpp_info["pkgconf"].rootpath.replace("\\", "/")):
                raise ConanException("pkgconf executable not found")

            with tools.environment_append({"PKG_CONFIG_PATH": os.path.join(self.source_folder, os.pardir, "test_package")}):
                self.run("{} libexample1 --libs".format(os.environ["PKG_CONFIG"]), run_environment=True)
                self.run("{} libexample1 --cflags".format(os.environ["PKG_CONFIG"]), run_environment=True)
