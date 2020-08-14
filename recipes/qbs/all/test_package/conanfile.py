from six import StringIO
from conans import ConanFile, tools

class QbsTestConan(ConanFile):
    settings = {
        "arch": ["x86_64"],
        "os": ["Linux", "Macos", "Windows"]
    }

    def build(self):
        args = ["--file %s" % self.source_folder]
        self.run("qbs build %s" % " ".join(args), run_environment=True)

    def test(self):
        if not tools.cross_building(self.settings):
            # Run the build result
            self.run("qbs run -p test", run_environment=True)

            output = StringIO()
            self.run("qbs show-version", run_environment=True)
            self.run("qbs show-version", output=output, run_environment=True)
            output_str = str(output.getvalue())
            self.output.info("Installed version: {}".format(output_str))
            require_version = str(self.deps_cpp_info["qbs"].version)
            self.output.info("Expected version: {}".format(require_version))
            assert(require_version in output_str)
