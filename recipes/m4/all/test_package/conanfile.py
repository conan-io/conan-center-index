from conan import ConanFile
from conan.tools.files import save
from io import StringIO
import os
import textwrap


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    @property
    def _m4_input_path(self):
        return os.path.join(self.build_folder, "input.m4")

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def build(self):
        save(self, self._m4_input_path, textwrap.dedent("""\
            m4_define(NAME1, `Harry, Jr.')
            m4_define(NAME2, `Sally')
            m4_define(MET, `$1 met $2')
            MET(`NAME1', `NAME2')
        """))

    def test(self):
        self.run("m4 --version")
        self.run(f"m4 -P {self._m4_input_path}")

        self.run(f"m4 -R {self.source_folder}/frozen.m4f {self.source_folder}/test.m4")

        output = StringIO()
        self.run(f"m4 -P {self._m4_input_path}", output=output)
        assert "Harry, Jr. met Sally" in output.getvalue()
