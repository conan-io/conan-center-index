from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        self.build_requires("automake/1.16.5")

    def build(self):
        shutil.copy(os.path.join(self.source_folder, "configure.ac"), os.path.join(self.build_folder, "configure.ac"))
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = [
            "--enable-option-checking=fatal",
            "--enable-gtk-doc=no",
        ]
        autotools.configure(args=args)

    def test(self):
        self.run("gtkdocize --copy", run_environment=True, win_bash=tools.os_info.is_windows)
