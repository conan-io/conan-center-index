from conan import ConanFile
from conan.tools.files import save, load, mkdir, chdir
from conan.tools.build import cross_building
from io import StringIO
import os
import json
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    @property
    def _binutils_data(self):
        return json.loads(load(self, "binutils_data"))

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _target_arch(self):
        return self._binutils_data["target_arch"]

    @property
    def _target_os(self):
        return self._binutils_data["target_os"]

    @property
    def _recipe_path(self):
        return self._binutils_data["recipe_path"]

    @property
    def _package_folder(self):
        return self._binutils_data["package_folder"]

    @property
    def _package_version(self):
        return self._binutils_data["version"]

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
        return os.path.join(self.source_folder, "..", "test_package_files", f"{self._target_os}-{part_arch}.s")

    def _append_gnu_triplet(self, exe):
        return f"{self._binutils_data['prefix']}{exe}"

    def generate(self):
        binutils_info = [v for k, v in self.dependencies.items() if repr(k.ref) == self.tested_reference_str]
        # for conan v1
        if not binutils_info:
            binutils_info = [v for k, v in self.dependencies.items() if str(k.ref) == self.tested_reference_str]
        binutils_info = binutils_info[0]
        binutils_opts = binutils_info.options
        binutils_ci = binutils_info.conf_info
        save(self, "binutils_data", json.dumps(
            {"target_arch": str(binutils_opts.target_arch), "target_os": str(binutils_opts.target_os),
             "prefix": str(binutils_ci.get("user:prefix")), "recipe_path": str(binutils_ci.get("user:recipe_path")),
             "package_folder": str(binutils_info.package_folder), "version": str(binutils_info.ref.version)}))

    def build(self):
        if not cross_building(self):
            if not os.path.isfile(self._test_package_assembly_source):
                self.output.warn(f"Missing {self._test_package_assembly_source}.\ntest_package does not support this target os/arch. Please consider adding it. (It's a great learning experience)")
            else:
                mkdir(self, os.path.join(self.build_folder, "bin"))
                mkdir(self, os.path.join(self.build_folder, "lib"))

                gas = self._append_gnu_triplet("as")
                ld = self._append_gnu_triplet("ld")
                extension = ""
                if self._target_os == "Windows":
                    extension = ".exe"

                    # Create minimum import library for kernel32.dll
                    dlltool = f"{self.deps_user_info['binutils'].gnu_triplet}-dlltool"

                    dlltool_args = [dlltool, "--input-def", f"{self.source_folder}/Windows-kernel32.def", "--output-lib", f"{self.build_folder}/lib/libkernel32.a"]
                    self.run(" ".join(dlltool_args))


                assembler_args = [gas, self._test_package_assembly_source, "-o", f"{self.build_folder}/object.o"]
                linker_args = [ld, f"{self.build_folder}/object.o", "-o", f"{self.build_folder}/bin/test_package{extension}"] + self._test_linker_args

                self.run(" ".join(assembler_args))
                self.run(" ".join(linker_args))

    def _can_run_target(self):
        if self._settings_build.os != self._target_os:
            return False
        if self._settings_build.arch == "x86_64":
            return self._target_arch in ("x86", "x86_64")
        return self._settings_build.arch == self._target_arch

    def _has_as(self):
        if self._target_os in ("Macos"):
            return False
        return True

    def _has_ld(self):
        if self._target_os in ("Macos"):
            return False
        return True

    def test(self):
        # Run selftest (conversion between conan os/arch <=> gnu triplet)
        recipe_path = self._recipe_path
        with chdir(self, os.path.dirname(recipe_path)):
            self.run(f"{sys.executable} -m unittest {os.path.basename(recipe_path)} --verbose")

        if not cross_building(self):
            if self._can_run_target() and os.path.isfile(self._test_package_assembly_source):
                output = StringIO()
                self.run(os.path.join("bin", "test_package"), output)
                text = output.getvalue()
                print(text)
                assert "Hello, world!" in text

            bins = ["ar", "nm", "objcopy", "objdump", "ranlib", "readelf", "strip"]
            if self._has_as():
                bins.append("as")
            if self._has_ld():
                bins.append("ld")

            for binary in bins:
                bin_path = StringIO()
                command = f'import os, shutil; print(os.path.realpath(shutil.which("{binary}")))'
                self.run(f"{sys.executable} -c '{command}'", bin_path)
                bin_path = bin_path.getvalue().strip()
                self.output.info(f"Found {binary} at {bin_path}")
                assert bin_path.startswith(self._package_folder)

                output = StringIO()
                self.run(f"{bin_path} --version", output)
                text = output.getvalue()
                print(text)
                assert self._package_version in text
