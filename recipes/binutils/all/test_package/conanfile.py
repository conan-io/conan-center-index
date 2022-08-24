from conan import ConanFile, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _target_arch(self):
        return str(self.options["binutils"].target_arch)

    @property
    def _target_os(self):
        return str(self.options["binutils"].target_os)

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
        return f"{self.deps_user_info['binutils'].prefix}{exe}"

    def build(self):
        if not tools.build.cross_building(self, self):

            if not os.path.isfile(self._test_package_assembly_source):
                self.output.warn(f"Missing {self._test_package_assembly_source}.\ntest_package does not support this target os/arch. Please consider adding it. (It's a great learning experience)")
            else:
                tools.files.mkdir(self, os.path.join(self.build_folder, "bin"))
                tools.files.mkdir(self, os.path.join(self.build_folder, "lib"))

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
        with tools.files.chdir(self, os.path.dirname(self.deps_user_info["binutils"].recipe_path)):
            self.run(f"python -m unittest {os.path.basename(self.deps_user_info['binutils'].recipe_path)} --verbose")

        if not tools.build.cross_building(self, self):
            if self._can_run_target() and os.path.isfile(self._test_package_assembly_source):
                output = StringIO()
                self.run(os.path.join("bin", "test_package"), output=output)
                text = output.getvalue()
                print(text)
                assert "Hello, world!" in text

            bins = ["ar", "nm", "objcopy", "objdump", "ranlib", "readelf", "strip"]
            if self._has_as():
                bins.append("as")
            if self._has_ld():
                bins.append("ld")

            for bin in bins:
                bin_path = os.path.realpath(tools.which(bin))
                self.output.info(f"Found {bin} at {bin_path}")
                assert bin_path.startswith(self.deps_cpp_info["binutils"].rootpath)

                output = StringIO()
                self.run("{} --version".format(bin_path), run_environment=True, output=output)
                text = output.getvalue()
                print(text)
                assert str(self.requires["binutils"].ref.version) in text
