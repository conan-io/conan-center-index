from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.layout import basic_layout

import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"
    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self)

    def generate(self):
        CMakeDeps(self).generate()
        CMakeToolchain(self).generate()

    def _build_ltdl(self):
        """ Build library using ltdl library """
        cmake = CMake(self)
        cmake.configure(build_script_folder="ltdl")
        cmake.build()

    def _test_ltdl(self):
        """ Test library using ltdl library"""
        lib_suffix = {
            "Linux": "so",
            "FreeBSD": "so",
            "Macos": "dylib",
            "Windows": "dll",
        }[str(self.settings.os)]

        if not cross_building(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            lib_path = os.path.join(self.cpp.build.bindirs[0], f"liba.{lib_suffix}")
            self.run(f"{bin_path} {lib_path}", env="conanrun")

    def build(self):
        self._build_ltdl()

    def test(self):
        self._test_ltdl()
