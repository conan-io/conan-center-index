from conans import ConanFile, tools
from contextlib import contextmanager
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "a.cpp", "b.cpp", "main.c", "main.cpp", "wscript"

    def build(self):
        if tools.build.cross_building(self, self.settings):
            return

        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)

        waf_path = tools.which("waf")
        if waf_path:
            waf_path = waf_path.replace("\\", "/")
            assert waf_path.startswith(str(self.deps_cpp_info["waf"].rootpath))

        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            self.run("waf -h")
            self.run("waf configure")
            self.run("waf")

    @contextmanager
    def _add_ld_search_path(self):
        env = {}
        if self.settings.os == "Linux":
            env["LD_LIBRARY_PATH"] = [os.path.join(os.getcwd(), "build")]
        elif self.settings.os == "Macos":
            env["DYLD_LIBRARY_PATH"] = [os.path.join(os.getcwd(), "build")]
        with tools.environment_append(env):
            yield

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            with self._add_ld_search_path():
                self.run(os.path.join("build", "app"), run_environment=True)
                self.run(os.path.join("build", "app2"), run_environment=True)
