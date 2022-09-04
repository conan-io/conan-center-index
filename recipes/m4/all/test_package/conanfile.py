import textwrap
from io import StringIO
from os import path

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.files import save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"

    @property
    def _m4_input_path(self):
        return path.join(self.build_folder, "input.m4")

    def build(self):
        save(self, self._m4_input_path, textwrap.dedent("""\
            m4_define(NAME1, `Harry, Jr.')
            m4_define(NAME2, `Sally')
            m4_define(MET, `$1 met $2')
            MET(`NAME1', `NAME2')
        """))

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            self.run(f"m4 --version", run_environment=True, env="conanbuild")
            self.run(f"m4 -R {path.join(self.source_folder, 'frozen.m4f')} {path.join(self.source_folder, 'test.m4')}", run_environment=True, env="conanbuild")

            output = StringIO()
            self.run(f"m4 -P {self._m4_input_path}", output=output, run_environment=True, env="conanbuild")

            assert "Harry, Jr. met Sally" in output.getvalue()
