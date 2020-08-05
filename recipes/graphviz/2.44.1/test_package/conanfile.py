import os, re
from six import StringIO
from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "os_build"

    def test(self):
        if not tools.cross_building(self.settings):
            output = StringIO()
            self.run("dot -V", output=output, run_environment=True)
            regex = r"(?<=dot - graphviz version )\d.\d{2}.\d"
            installed_version = re.search(regex, str(output.getvalue()))[0]
            self.output.info("Installed version: {}".format(installed_version))
            expected_version = str(self.deps_cpp_info["graphviz"].version)
            self.output.info("Expected version:  {}".format(expected_version))
            assert(expected_version in installed_version)
