from conan import ConanFile, tools$
from io import StringIO


class TestPackage(ConanFile):
    settings = "os", "arch"

    def build(self):
        pass # nothing to build, but tests should not warn

    def test(self):
        if tools.build.cross_building(self, self):
            return
            # OK, this needs some explanation
            # You basically do not crosscompile that package, never
            # But C3I does, Macos x86_64 to M1,
            # and this is why there is some cross compilation going on
            # The test will not work in that environment, so .... don't test
        test_cmd = ['java', '--version']
        output = StringIO()
        self.run(test_cmd, output=output, run_environment=True)
        version_info = output.getvalue()
        if "Zulu" in version_info:
            pass
        else:
            raise Exception("java call seems not use the Zulu bin")
