from conan import ConanFile
from conan.tools.build import can_run
from conan.errors import ConanException
from io import StringIO

required_conan_version = ">=1.47.0"


class TestPackage(ConanFile):
    test_type = "explicit"
    settings = "os", "arch"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        pass  # nothing to build, but tests should not warn

    def test(self):
        if can_run(self):
            output = StringIO()
            self.run("java --version", output, env="conanrun")
            self.output.info(f"Java version output: {output.getvalue()}")
            version_info = output.getvalue()
            if "openjdk" in version_info:
                pass
            else:
                raise ConanException("java call seems not use the openjdk bin")
