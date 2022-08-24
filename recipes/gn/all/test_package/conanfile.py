from conan import ConanFile, tools
from conans import CMake
from contextlib import contextmanager
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("ninja/1.10.2")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                yield
        else:
            compiler_defaults = {}
            if self.settings.compiler == "gcc":
                compiler_defaults = {
                    "CC": "gcc",
                    "CXX": "g++",
                    "AR": "ar",
                    "LD": "g++",
                }
            elif self.settings.compiler in ("apple-clang", "clang"):
                compiler_defaults = {
                    "CC": "clang",
                    "CXX": "clang++",
                    "AR": "ar",
                    "LD": "clang++",
                }
            env = {}
            for k in ("CC", "CXX", "AR", "LD"):
                v = tools.get_env(k, compiler_defaults.get(k, None))
                if v:
                    env[k] = v
            with tools.environment_append(env):
                yield

    @property
    def _target_os(self):
        if tools.is_apple_os(self.settings.os):
            return "mac"
        # Assume gn knows about the os
        return {
            "Windows": "win",
        }.get(str(self.settings.os), str(self.settings.os).lower())

    @property
    def _target_cpu(self):
        return {
            "x86_64": "x64",
        }.get(str(self.settings.arch), str(self.settings.arch))

    def build(self):
        if not tools.build.cross_building(self, self.settings):
            with tools.files.chdir(self, self.source_folder):
                gn_args = [
                    os.path.relpath(os.path.join(self.build_folder, "bin"), os.getcwd()).replace("\\", "/"),
                    "--args=\"target_os=\\\"{os_}\\\" target_cpu=\\\"{cpu}\\\"\"".format(os_=self._target_os, cpu=self._target_cpu),
                ]
                self.run("gn gen {}".format(" ".join(gn_args)), run_environment=True)
            with self._build_context():
                self.run("ninja -v -j{} -C bin".format(tools.cpu_count(self, )), run_environment=True)

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
