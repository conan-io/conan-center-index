from conan import ConanFile
from conan.tools.build import build_jobs, cross_building
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def tested_reference_version(self):
        return str(self.dependencies["scons"].ref.version)

    def build(self):
        scons_path = os.path.join(self.dependencies["scons"].package_folder, "bin", "scons")

        output = StringIO()
        self.run("{} --version".format(scons_path), output)
        self.output.info("Installed version: {}".format(output.getvalue()))
        assert(self.tested_reference_version in output.getvalue())

        self.run("scons --version", output)
        assert(self.tested_reference_version in output.getvalue())

        scons_args = [
            "-j", str(build_jobs(self)),
            "-C", self.source_folder,
            "-f", os.path.join(self.source_folder, "SConstruct"),
        ]

        self.run("scons {}".format(" ".join(scons_args)), env="conanrun")

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(".", "test_package")
            output = StringIO()
            self.run(bin_path, output)
            self.output.info("output: {}".format(output.getvalue()))
            self.run(bin_path)
