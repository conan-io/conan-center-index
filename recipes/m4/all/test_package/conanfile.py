import os
import textwrap
from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    @property
    def _m4_input_path(self):
        return os.path.join(self.build_folder, "input.m4")

    def build(self):
        save(self, self._m4_input_path, textwrap.dedent("""\
            m4_define(NAME1, `Harry, Jr.')
            m4_define(NAME2, `Sally')
            m4_define(MET, `$1 met $2')
            MET(`NAME1', `NAME2')
        """))

    def test(self):
        if can_run(self):
            m4_bin = os.path.join(self.deps_cpp_info["m4"].rootpath, "bin", "m4")
            self.run(f"{m4_bin} --version", env="conanbuild")
            self.run(f"{m4_bin} -P {self._m4_input_path}", env="conanbuild")

            self.run(f"{m4_bin} -R {os.path.join(self.source_folder, 'frozen.m4f')} {os.path.join(self.source_folder, 'test.m4')}", env="conanbuild")

            output = StringIO()
            self.run(f"{m4_bin} -P {self._m4_input_path}", output=output, env="conanbuild")

            assert "Harry, Jr. met Sally" in output.getvalue()
