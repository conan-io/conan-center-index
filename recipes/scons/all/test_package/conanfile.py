from conans import ConanFile, tools
from conans.errors import ConanException
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "scons"

    def build(self):
        scons_path = self.deps_user_info["scons"].scons
        if not scons_path:
            raise ConanException("scons could not be found")
        if not scons_path.replace("\\", "/").startswith(self.deps_cpp_info["scons"].rootpath.replace("\\", "/")):
            raise ConanException("an external scons was found")

        output = StringIO()
        self.run("{} --version".format(scons_path), run_environment=True, output=output, ignore_errors=True)
        self.output.info("output: %s" % output.getvalue())
        output = StringIO()
        self.run("{} --version".format(scons_path), run_environment=True, output=output)
        text = output.getvalue()
        if self.deps_cpp_info["scons"].version not in text:
            raise ConanException("scons --version does not return correct version")

        scons_args = [
            "-j", str(tools.cpu_count(self, )),
            "-C", self.source_folder,
            "-f", os.path.join(self.source_folder, "SConstruct"),
        ]

        self.run("scons {}".format(" ".join(scons_args)), run_environment=True)

    def test(self):
        from io import StringIO

        if not tools.build.cross_building(self, self):
            bin_path = os.path.join(".", "test_package")
            output = StringIO()
            self.run(bin_path, run_environment=True, ignore_errors=True, output=output)
            self.output.info("output: %s" % output.getvalue())
            self.run(bin_path, run_environment=True)
