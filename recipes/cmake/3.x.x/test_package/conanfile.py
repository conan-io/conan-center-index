from six import StringIO
from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            output = StringIO()
            # Third arg to self.run renamed "stdout" in Conan 2.0 but 1.x linter doesn't like it
            self.run("cmake --version", output, env="conanrun")
            output_str = str(output.getvalue())
            self.output.info("Installed version: {}".format(output_str))
            tokens = self.tested_reference_str.split("@", 1)
            name, require_version = tokens[0].split("/", 1)
            self.output.info("Expected version: {}".format(require_version))
            assert_cmake_version = "cmake version %s" % require_version
            assert(assert_cmake_version in output_str)
