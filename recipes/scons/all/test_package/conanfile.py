from conans import ConanFile, tools
from conans.errors import ConanException
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "scons"

    def build(self):
        scons_path = tools.which("scons")
        assert scons_path.replace("\\", "/").startswith(self.deps_cpp_info["scons"].rootpath.replace("\\", "/"))

        output = StringIO()
        self.run("{} --version".format(scons_path), run_environment=True, output=output)
        text = output.getvalue()
        if self.deps_cpp_info["scons"].version not in text:
            raise ConanException("scons --version does not return correct version")

        self.output.info("TMP={}".format(os.environ.get("TMP")))

        self.run("scons -C \"{}\"".format(self.source_folder))

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
