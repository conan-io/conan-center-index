from conans import ConanFile, tools
from conans.errors import ConanException
from io import StringIO

required_conan_version = ">=1.36.0"


class TestPackage(ConanFile):
    test_type = "build_requires"

    def build(self):
        pass  # nothing to build, but tests should not warn

    def test(self):
        if not tools.cross_building(self):
            output = StringIO()
            self.run("java --version", output=output, run_environment=True)
            print(output.getvalue)
            version_info = output.getvalue()
            if "openjdk" in version_info:
                pass
            else:
                raise ConanException("java call seems not use the openjdk bin")
