from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import shutil

required_conan_version = ">=1.36.0"

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "configure.ac", "Makefile.am", "hello.c"
    test_type = "build_requires"

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure()
        autotools.make()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join(".", "hello"))
