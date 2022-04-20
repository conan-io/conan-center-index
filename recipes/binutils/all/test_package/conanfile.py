from conans import ConanFile, tools
from conans.errors import ConanException
from io import StringIO
import os
import shlex


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
        return os.path.join(self.source_folder, f"{self._target_os}-{self._target_arch}.s")

    def build(self):
        if not tools.cross_building(self):

            if not os.path.isfile(self._test_package_assembly_source):
                self.output.warn(f"Test is missing a test for this target ({self._test_package_assembly_source}. Please consider adding one. (It's a great learning experience)")
            else:
                tools.mkdir(os.path.join(self.build_folder, "bin"))
                tools.mkdir(os.path.join(self.build_folder, "lib"))

                gas = f"{self.deps_user_info['binutils'].gnu_triplet}-as"
                ld = f"{self.deps_user_info['binutils'].gnu_triplet}-ld"
                extension = ""
                if self._target_os == "Windows":
                    extension = ".exe"

                    # Create minimum import library for kernel32.dll
                    dlltool = f"{self.deps_user_info['binutils'].gnu_triplet}-dlltool"

                    dlltool_args = [dlltool, "--input-def", f"{self.source_folder}/Windows-kernel32.def", "--output-lib", f"{self.build_folder}/lib/libkernel32.a"]
                    self.run(shlex.join(dlltool_args))


                assembler_args = [gas, self._test_package_assembly_source, "-o", f"{self.build_folder}/object.o"]
                linker_args = [ld, f"{self.build_folder}/object.o", "-o", f"{self.build_folder}/bin/test_package{extension}"] + self._test_linker_args

                self.run(shlex.join(assembler_args))
                self.run(shlex.join(linker_args))

    def _can_run_target(self):
        if self._settings_build.os != self._target_os:
            return False
        if self._settings_build.arch == "x86_64":
            return self._target_arch in ("x86", "x86_64")
        return self._settings_build.arch == self._target_arch

    def test(self):
        if not tools.cross_building(self):
            if self._can_run_target() and os.path.isfile(self._test_package_assembly_source):
                output = StringIO()
                self.run(os.path.join("bin", "test_package"), output=output)
                text = output.getvalue()
                print(text)
                assert "Hello, world!" in text

            bins = ["ar", "as", "ld", "nm", "objcopy", "objdump", "ranlib", "readelf", "strip"]
            for bin in bins:
                bin_path = os.path.realpath(tools.which(bin))
                print(f"Found {bin} at {bin_path}")
                assert bin_path.startswith(self.deps_cpp_info["binutils"].rootpath)

                output = StringIO()
                self.run("{} --version".format(bin_path), run_environment=True, output=output)
                text = output.getvalue()
                print(text)
                assert str(self.requires["binutils"].ref.version) in text
