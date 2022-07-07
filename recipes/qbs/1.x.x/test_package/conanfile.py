from six import StringIO
from conan import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        output = StringIO()
        self.run("qbs --version", output=output, run_environment=True)
        output_str = str(output.getvalue()).strip()
        self.output.info(f"Installed version: {output_str}")
        require_version = str(self.deps_cpp_info["qbs"].version)
        self.output.info(f"Expected version: {require_version}")
        assert require_version == output_str
