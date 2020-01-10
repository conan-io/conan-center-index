import os
from six import StringIO
from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    def test(self):
        if not tools.cross_building(self.settings):
            output = StringIO()
            self.output.info(self.deps_env_info["cmake"].CMAKE_ROOT)
            # cmake_path = os.path.abspath(os.path.join(self.deps_cpp_info["cmake"].rootpath, "bin"))
            self.run("cmake --version", output=output, run_environment=True)
            self.output.info("Installed: %s" % str(output.getvalue()))
            ver = str(self.requires["cmake"].ref.version)
            value = str(output.getvalue())
            cmake_version = value.split('\n')[0]
            self.output.info("Expected value: {}".format(ver))
            self.output.info("Detected value: {}".format(cmake_version))
            assert(ver in cmake_version)
