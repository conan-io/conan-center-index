import os
import shlex
import sys
from io import StringIO
from shutil import which

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, mkdir
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def layout(self):
        basic_layout(self, ".")

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _target_arch(self):
        return str(self.dependencies.build[self.tested_reference_str].options.target_arch)

    @property
    def _target_os(self):
        return str(self.dependencies.build[self.tested_reference_str].options.target_os)

    @property
    def _gnu_triplet(self):
        return str(self.dependencies.build[self.tested_reference_str].conf_info.get('user.binutils:gnu_triplet'))

    @property
    def _prefix(self):
        return str(self.dependencies.build[self.tested_reference_str].conf_info.get('user.binutils:prefix'))

    @property
    def _test_linker_args(self):
        args = []
        if self._target_os == "Windows":
            args.extend(["--subsystem", "console", f"{self.build_folder}/lib/libkernel32.a"])
        return args

    @property
    def _test_package_assembly_source(self):
        part_arch = self._target_arch
        if "armv7" in part_arch:
            part_arch = "armv7"
        elif part_arch in ("riscv32", "riscv64"):
            part_arch = "riscv"
        return os.path.join(self.source_folder, f"{self._target_os}-{part_arch}.s")

    def _append_gnu_triplet(self, exe):
        return f"{self._prefix}{exe}"

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):

        # FIXME: move to ConanFile.test
        #        ConanFile.dependencies is not aviable in conan v1 inside ConanFile.test
        # Run selftest (conversion between conan os/arch <=> gnu triplet)
        recipe_path = str(self.dependencies.build[self.tested_reference_str].conf_info.get('user.binutils:recipe_path'))
        with chdir(self, os.path.dirname(recipe_path)):
            unittest_args = [sys.executable, "-m", "unittest", os.path.basename(recipe_path), "--verbose"]
            self.run(shlex.join(unittest_args), env="conanrun")

        if not os.path.isfile(self._test_package_assembly_source):
            self.output.warning(f"Missing {self._test_package_assembly_source}.\ntest_package does not support this target os/arch. Please consider adding it. (It's a great learning experience)")
            return

        mkdir(self, os.path.join(self.build_folder, "bin"))
        mkdir(self, os.path.join(self.build_folder, "lib"))

        gas = self._append_gnu_triplet("as")
        ld = self._append_gnu_triplet("ld")
        extension = ""
        if self._target_os == "Windows":
            extension = ".exe"

            # Create minimum import library for kernel32.dll
            dlltool = f"{self._gnu_triplet}-dlltool{extension}"

            dlltool_args = [dlltool, "--input-def", f"{self.source_folder}/Windows-kernel32.def", "--output-lib", f"{self.build_folder}/lib/libkernel32.a"]
            self.run(shlex.join(dlltool_args), env="conanbuild")

        assembler_args = [gas, self._test_package_assembly_source, "-o", f"{self.build_folder}/object.o"]
        linker_args = [ld, f"{self.build_folder}/object.o", "-o", f"{self.build_folder}/bin/test_package{extension}"] + self._test_linker_args

        self.run(shlex.join(assembler_args), env="conanbuild")
        self.run(shlex.join(linker_args), env="conanbuild")

        binaries = ["ar", "nm", "objcopy", "objdump", "ranlib", "readelf", "strip"]
        if self._has_as():
            binaries.append("as")
        if self._has_ld():
            binaries.append("ld")

        # FIXME: move to ConanFile.test
        #        ConanFile.dependencies is not aviable in conan v1 inside ConanFile.test
        bindirs = VirtualBuildEnv(self).vars().get("PATH")
        for binary in binaries:
            bin_path = os.path.realpath(which(binary, path=bindirs))
            self.output.info(f"Found {binary} at {bin_path}")
            assert bin_path.startswith(self.dependencies.build[self.tested_reference_str].package_folder), "Binary was fount outside the conan cache"

            output = StringIO()
            self.run(shlex.join([bin_path, "--version"]), env="conanbuild", stdout=output)
            text = output.getvalue()
            self.output.info(f"Version: {text.splitlines()[0]}")
            assert str(self.dependencies.build[self.tested_reference_str].ref.version) in text

    def _can_run_target(self):
        if self._settings_build.os != self._target_os:
            return False
        if self._settings_build.arch == "x86_64":
            return self._target_arch in ("x86", "x86_64")
        return self._settings_build.arch == self._target_arch

    def _has_as(self):
        if self._target_os in ("Macos",):
            return False
        return True

    def _has_ld(self):
        if self._target_os in ("Macos",):
            return False
        return True

    def test(self):
        if can_run(self):
            extension = ""
            if self._target_os == "Windows":
                extension = ".exe"
            exe = os.path.join(self.cpp_info.bindirs[0], f"test_package{extension}")
            if self._can_run_target() and os.path.isfile(exe):
                output = StringIO()
                self.run(exe, stdout=output, env="conanrun")
                text = output.getvalue()
                assert "Hello, world!" in text
