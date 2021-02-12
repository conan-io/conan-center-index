from conans import ConanFile, tools
from conans.errors import ConanException
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

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("msys2/20200517")

    def build(self):
        tools.save(self._m4_input_path, M4_CONTENTS)

    def test(self):
        m4_bin = tools.get_env("M4")
        if m4_bin is None or not m4_bin.startswith(self.deps_cpp_info["m4"].rootpath):
            raise ConanException("M4 environment variable not set")

        if not tools.cross_building(self.settings):
            self.run("{} --version".format(m4_bin), run_environment=True)
            self.run("{} -P {}".format(m4_bin, self._m4_input_path))

            self.run("m4 -R {0}/frozen.m4f {0}/test.m4".format(self.source_folder), run_environment=True)

            output = StringIO()
            self.run("{} -P {}".format(m4_bin, self._m4_input_path), output=output)

            assert "Harry, Jr. met Sally" in output.getvalue()
