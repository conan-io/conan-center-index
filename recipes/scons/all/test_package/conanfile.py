from conans import ConanFile, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "scons"

    _script_tool = {
        "gcc": "gcc",
        "clang": "clang",
        "Visual Studio": "msvc",
        "apple-clang": "clang",
    }

    def build(self):
        scons_path = tools.which("scons")
        assert scons_path.replace("\\", "/").startswith(self.deps_cpp_info["scons"].rootpath.replace("\\", "/"))

        output = StringIO()
        self.run("{} --version".format(scons_path), run_environment=True, output=output)
        text = output.getvalue()
        print(text)
        assert self.requires["scons"].ref.version in text

        self.output.info("TMP={}".format(os.environ.get("TMP")))

        self.run("scons -C \"{}\" --conan-compiler={}".format(self.source_folder, self._script_tool[str(self.settings.compiler)]))

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
