import os
import shutil
from contextlib import contextmanager

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"
    exports_sources = "a.cpp", "b.cpp", "main.c", "main.cpp", "wscript"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        if not can_run(self):
            return

        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)

        with chdir(self, self.build_folder):
            self.run("waf -h")
            self.run("waf configure")
            self.run("waf")

    @contextmanager
    def _add_ld_search_path(self, extra_path):
        if self.settings.os in ["Linux", "FreeBSD"]:
            var = "LD_LIBRARY_PATH"
        elif is_apple_os(self):
            var = "DYLD_LIBRARY_PATH"
        else:
            yield
            return
        ld_path = os.environ.get(var, "")
        os.environ[var] = f"{ld_path}{os.pathsep}{extra_path}"
        yield
        os.environ[var] = ld_path

    def test(self):
        if not can_run(self):
            return
        bin_dir = os.path.join(self.cpp.build.bindir, "build")
        with self._add_ld_search_path(bin_dir):
            bin_path = os.path.join(bin_dir, "app")
            self.run(bin_path, env="conanrun")
            bin_path = os.path.join(bin_dir, "app2")
            self.run(bin_path, env="conanrun")
