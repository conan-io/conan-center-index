from conans import ConanFile, tools
from conans.errors import ConanException
from io import StringIO
import os
import textwrap


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _m4_input_path(self):
        return os.path.join(self.build_folder, "input.m4")

    def build(self):
        tools.files.save(self, self._m4_input_path, textwrap.dedent("""\
            m4_define(NAME1, `Harry, Jr.')
            m4_define(NAME2, `Sally')
            m4_define(MET, `$1 met $2')
            MET(`NAME1', `NAME2')
        """))

    def test(self):
        if hasattr(self, "settings_build"):
            exe_suffix = ".exe" if self.settings.os == "Windows" else ""
            m4_bin = os.path.join(self.deps_cpp_info["m4"].rootpath, "bin", "m4" + exe_suffix)
        else:
            m4_bin = tools.get_env("M4")
            if m4_bin is None or not m4_bin.startswith(self.deps_cpp_info["m4"].rootpath):
                raise ConanException("M4 environment variable not set")

        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("{} --version".format(m4_bin), run_environment=True)
            self.run("{} -P {}".format(m4_bin, self._m4_input_path))

            self.run("m4 -R {0}/frozen.m4f {0}/test.m4".format(self.source_folder), run_environment=True)

            output = StringIO()
            self.run("{} -P {}".format(m4_bin, self._m4_input_path), output=output)

            assert "Harry, Jr. met Sally" in output.getvalue()
