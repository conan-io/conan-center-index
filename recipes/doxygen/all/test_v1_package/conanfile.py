from conans import ConanFile, tools
from conans.errors import ConanException
from six import StringIO


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self):
            self.output.info("Doxygen Version:")
            stringio = StringIO()
            try:
                self.run(f"{self.recipe_folder}/doxygen --version", run_environment=True, output=stringio)
            except ConanException:
                # FIXME: Doxygen is built with glibc 2.29, but the CI machines have 2.23
                assert "version `GLIBC_2.29' not found" in stringio.getvalue()
