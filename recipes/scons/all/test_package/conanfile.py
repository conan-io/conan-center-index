from conan import ConanFile
from conan.tools.build import build_jobs, cross_building
from conan.tools.layout import basic_layout
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def build(self):
        output = StringIO()
        self.run("scons --version", output)
        self.output.info(output.getvalue())
        assert("SCons by Steven Knight" in output.getvalue())

        scons_args = [
            "-j", str(build_jobs(self)),
            "-C", self.source_folder,
            "-f", os.path.join(self.source_folder, "SConstruct"),
        ]

        self.run("scons {}".format(" ".join(scons_args)))

    def test(self):
        if not cross_building(self):
            # Scons build put executable righe here
            bin_path = os.path.join(self.recipe_folder, "test_package")
            self.run(bin_path, env="conanrun")
