import os
import shutil
from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    @property
    def file_io(self):
        return {
            "c": {
                "compiler": "$CC",
                "src": os.path.join(self.source_folder, "hello.c"),
                "bin": os.path.join(self.build_folder, "hello_c"),
            },
            "cpp": {
                "compiler": "$CXX",
                "src": os.path.join(self.source_folder, "hello.cpp"),
                "bin": os.path.join(self.build_folder, "hello_cpp"),
            },
            "fortran": {
                "compiler": "$FC",
                "src": os.path.join(self.source_folder, "hello.f90"),
                "bin": os.path.join(self.build_folder, "hello_f90"),
            },
        }

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        runenv = VirtualRunEnv(self)
        runenv.generate()

    def build(self):
        self.run("echo PATH: $PATH")
        for language, files in self.file_io.items():
            self.output.info(f"Testing build using {language} compiler")
            # Confirm compiler is propagated to env
            envvar = files["compiler"].split("$")[1]
            self.run(f"echo {envvar}: {files['compiler']}", env="conanbuild")
            self.run(f"{files['compiler']} --version", env="conanbuild")
            self.run(f"{files['compiler']} -dumpversion", env="conanbuild")

            # Confirm files can be compiled
            self.run(
                f"{files['compiler']} {files['src']} -o {files['bin']}",
                env="conanbuild",
            )
            self.output.info(f"Successfully built {files['bin']}")

    def test(self):
        def chmod_plus_x(name):
            if os.name == "posix":
                os.chmod(name, os.stat(name).st_mode | 0o111)

        for language, files in self.file_io.items():
            self.output.info(f"Testing application built using {language} compiler")
            if not cross_building(self):
                chmod_plus_x(f"{files['bin']}")

                if self.settings.os == "Linux":
                    if shutil.which("readelf"):
                        self.run(f"readelf -l {files['bin']}", env="conanrun")
                    else:
                        self.output.info(
                            "readelf is not on the PATH. Skipping readelf test."
                        )

                if self.settings.os == "Macos":
                    if shutil.which("otool"):
                        self.run(f"otool -L {files['bin']}", env="conanrun")
                    else:
                        self.output.info(
                            "otool is not on the PATH. Skipping otool test."
                        )

                self.run(f"{files['bin']}", env="conanrun")
