import os
from six import StringIO
from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os"

    def test(self):
        if not tools.cross_building(self.settings):
            output = StringIO()
            self.run("cmake --version", output=output, run_environment=True)
            output_str = str(output.getvalue())
            self.output.info("Installed version: {}".format(output_str))
            require_version = str(self.deps_cpp_info["cmake"].version)
            self.output.info("Expected version: {}".format(require_version))
            assert_cmake_version = "cmake version %s" % require_version
            assert(assert_cmake_version in output_str)
