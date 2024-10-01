from conan import ConanFile
from conan.tools.build import cross_building
from io import StringIO


class TestPackage(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        pass # nothing to build, but tests should not warn

    def test(self):
        if cross_building(self):
            return
            # OK, this needs some explanation
            # You basically do not crosscompile that package, never
            # But C3I does, Macos x86_64 to M1,
            # and this is why there is some cross compilation going on
            # The test will not work in that environment, so .... don't test
        output = StringIO()
        self.run("java --version", output, env="conanrun")
        version_info = output.getvalue()
        if "Zulu" not in version_info:
            raise Exception("java call seems not use the Zulu bin")
