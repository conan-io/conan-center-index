import os
from six import StringIO
from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    def test(self):
        if not tools.cross_building(self.settings):
            output = StringIO()
            cmake_path = os.path.join(self.deps_cpp_info["cmake"].rootpath, "bin", "cmake")
            self.run("{} --version".format(cmake_path), output=output, run_environment=True)
            self.output.info("Installed: %s" % str(output.getvalue()))
            if self.requires["cmake"].ref.version != "1.0":
                ver = str(self.requires["cmake"].ref.version)
            else:
                ver = str(self.options["cmake"].version)

            value = str(output.getvalue())
            cmake_version = value.split('\n')[0]
            self.output.info("Expected value: {}".format(ver))
            self.output.info("Detected value: {}".format(cmake_version))
            assert(ver in cmake_version)
