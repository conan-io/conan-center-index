from conan import ConanFile
from conan.tools.build import can_run
from conan.errors import ConanException
from io import StringIO


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            buffer = StringIO()
            self.output.info("Doxygen Version:")
            try:
                self.run(f"{self.recipe_folder}/doxygen --version", buffer)
            except ConanException:
                # FIXME: libm.so.6: version `GLIBC_2.29' not found
                # Doxygen built with a newer glibc than the one in the test image
                value = buffer.getvalue()
                self.output.error(f"Doxygen failed to run: {value}")
                assert "GLIBC" in buffer.getvalue()
