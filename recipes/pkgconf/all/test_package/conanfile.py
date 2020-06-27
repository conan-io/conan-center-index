from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from conans.errors import ConanException
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build_requirements(self):
        self.build_requires("automake/1.16.2")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def build(self):
        # Test pkg.m4 integration into automake
        shutil.copy(os.path.join(self.source_folder, "configure.ac"),
                    os.path.join(self.build_folder, "configure.ac"))
        self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure()

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)

            if not os.environ["PKG_CONFIG"].startswith(self.deps_cpp_info["pkgconf"].rootpath):
                raise ConanException("PKG_CONFIG variable incorrect")

            pkgconf_path = tools.which("pkgconf").replace("\\", "/")
            if not pkgconf_path.startswith(self.deps_cpp_info["pkgconf"].rootpath):
                raise ConanException("pkgconf executable not found")

            with tools.environment_append({"PKG_CONFIG_PATH": self.source_folder}):
                self.run("{} libexample1 --libs".format(os.environ["PKG_CONFIG"]), run_environment=True)
                self.run("{} libexample1 --cflags".format(os.environ["PKG_CONFIG"]), run_environment=True)
