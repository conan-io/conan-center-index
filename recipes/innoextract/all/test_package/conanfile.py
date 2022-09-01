from six import StringIO
from conan import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type", "compiler"

    def test(self):
        if not tools.build.cross_building(self):
            output = StringIO()
            self.run("innoextract --version", output=output,
                     run_environment=True)
            output_str = str(output.getvalue())
            self.output.info("Installed version: {}".format(output_str))
            require_version = str(self.deps_cpp_info["innoextract"].version)
            require_version = ".".join(require_version.split(".")[:2])
            self.output.info("Expected version: {}".format(require_version))
            assert_innoextract_version = "innoextract %s" % require_version
            assert(assert_innoextract_version in output_str)
