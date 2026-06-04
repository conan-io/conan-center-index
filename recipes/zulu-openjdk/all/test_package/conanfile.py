from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from io import StringIO


class TestPackage(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        pass

    def test(self):
        if can_run(self):
            output = StringIO()
            self.run("java --version", output, env="conanrun")
            version_info = output.getvalue()
            self.output.info(f"java --version returned: \n{version_info}")
            if "Zulu" not in version_info:
                raise ConanException("zulu-openjdk test package failed: 'Zulu' not found in java --version output")
