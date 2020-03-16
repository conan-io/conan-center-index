from conans import ConanFile, tools
from io import StringIO
import os


M4_CONTENTS = """\
m4_define(NAME1, `Harry, Jr.')
m4_define(NAME2, `Sally')
m4_define(MET, `$1 met $2')
MET(`NAME1', `NAME2')
"""


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _m4_input_path(self):
        return os.path.join(self.build_folder, "input.m4")

    def build(self):
        tools.save(self._m4_input_path, M4_CONTENTS)

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("{} --version".format(os.environ["M4"]), run_environment=True)
            self.run("{} -P {}".format(os.environ["M4"], self._m4_input_path))

            output = StringIO()
            self.run("{} -P {}".format(os.environ["M4"], self._m4_input_path), output=output)

            assert "Harry, Jr. met Sally" in output.getvalue()
