from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import conan.tools.files as tools_files
import os
import sys
import textwrap
import time

required_conan_version = ">=1.33.0"


class GnConan(ConanFile):
    name = "gn"
    description = "GN is a meta-build system that generates build files for Ninja."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("gn", "build", "system", "ninja")
    license = "BSD-3-Clause"
    homepage = "https://gn.googlesource.com/"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_compiler_version_supporting_cxx17(self):
        return {
            "Visual Studio": 15,
            "gcc": 7,
            "clang": 4,
            "apple-clang": 10,
        }.get(str(self.settings.compiler))

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        else:
            if self._minimum_compiler_version_supporting_cxx17:
                if tools.Version(self.settings.compiler.version) < self._minimum_compiler_version_supporting_cxx17:
                    raise ConanInvalidConfiguration("gn requires a compiler supporting c++17")
            else:
                self.output.warn("gn recipe does not recognize the compiler. gn requires a compiler supporting c++17. Assuming it does.")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools_files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder)

    def build_requirements(self):
        # FIXME: add cpython build requirements for `build/gen.py`.
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
            elif self.settings.compiler == "clang":
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

    @staticmethod
    def _to_gn_platform(os_, compiler):
        if tools.is_apple_os(os_):
            return "darwin"
        if compiler == "Visual Studio":
            return "msvc"
        # Assume gn knows about the os
        return str(os_).lower()

    def build(self):
        with tools.chdir(self._source_subfolder):
            with self._build_context():
                # Generate dummy header to be able to run `build/ben.py` with `--no-last-commit-position`. This allows running the script without the tree having to be a git checkout.
                tools.save(os.path.join("src", "gn", "last_commit_position.h"),
                           textwrap.dedent("""\
                                #pragma once
                                #define LAST_COMMIT_POSITION "1"
                                #define LAST_COMMIT_POSITION_NUM 1
                                """))
                conf_args = [
                    "--no-last-commit-position",
                    "--host={}".format(self._to_gn_platform(self.settings.os, self.settings.compiler)),
                ]
                if self.settings.build_type == "Debug":
                    conf_args.append("-d")
                self.run("{} build/gen.py {}".format(sys.executable, " ".join(conf_args)), run_environment=True)
                # Try sleeping one second to avoid time skew of the generated ninja.build file (and having to re-run build/gen.py)
                time.sleep(1)
                build_args = [
                    "-C", "out",
                    "-j{}".format(tools.cpu_count()),
                ]
                self.run("ninja {}".format(" ".join(build_args)), run_environment=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("gn", src=os.path.join(self._source_subfolder, "out"), dst="bin")
        self.copy("gn.exe", src=os.path.join(self._source_subfolder, "out"), dst="bin")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.includedirs = []
