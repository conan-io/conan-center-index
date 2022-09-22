from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
from conans import tools as tools_legacy
import os

from conan.errors import ConanException
from io import StringIO
import textwrap


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _cppfront_input_path(self):
        return os.path.join(self.build_folder, "pure2-hello.cpp2")
        # return os.path.join("pure2-hello.cpp2")

    def build(self):
        tools_legacy.save(self._cppfront_input_path, textwrap.dedent("""\
            main: () -> int = {
                std::cout << "Hello " << name() << "\\n";
            }

            name: () -> std::string = {
                s: std::string = "world";
                decorate(s);
                return s;
            }

            decorate: (inout s: std::string) = {
                s = "[" + s + "]";
            }
        """))

    def test(self):
        if hasattr(self, "settings_build"):
            exe_suffix = ".exe" if self.settings.os == "Windows" else ""
            cppfront_bin = os.path.join(self.deps_cpp_info["cppfront"].rootpath, "bin", "cppfront" + exe_suffix)
        else:
            cppfront_bin = tools_legacy.get_env("cppfront")
            if cppfront_bin is None or not cppfront_bin.startswith(self.deps_cpp_info["cppfront"].rootpath):
                raise ConanException("cppfront environment variable not set")

        self.output.info(f"************************* cppfront_bin: {cppfront_bin}")
        self.output.info(f"************************* self._cppfront_input_path: {self._cppfront_input_path}")


        if not tools_legacy.cross_building(self, skip_x64_x86=True):
            # self.run("f{cppfront_bin} --version", run_environment=True)
            # self.run("f{cppfront_bin} {self._cppfront_input_path}")
            self.run("{} {}".format(cppfront_bin, self._cppfront_input_path))

            # self.run("cppfront -R {0}/frozen.m4f {0}/test.m4".format(self.source_folder), run_environment=True)

            # output = StringIO()
            # self.run("{} -P {}".format(m4_bin, self._m4_input_path), output=output)

            # assert "Harry, Jr. met Sally" in output.getvalue()
