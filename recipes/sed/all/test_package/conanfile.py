from io import StringIO

from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        # --version is GNU specific: fails with BSD sed, so a system sed can't mask a broken package
        version = StringIO()
        self.run("sed --version", version)
        expected = f"sed (GNU sed) {self.dependencies.build['sed'].ref.version}"
        first_line = version.getvalue().splitlines()[0].strip()
        assert first_line == expected, f"expected '{expected}', got '{first_line}'"

        result = StringIO()
        self.run('echo "hello world" | sed "s/world/conan/"', result)
        assert result.getvalue().strip() == "hello conan", result.getvalue()
