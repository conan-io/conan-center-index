from conans import ConanFile, tools
import os


class TestPackgeConan(ConanFile):
    settings = "os", "arch", "compiler"

    @property
    def _toolset(self):
        if self.settings.compiler == "Visual Studio":
            return "msvc"
        elif self.settings.os == "Windows" and self.settings.compiler == "clang":
            return "clang-win"
        elif self.settings.os == "Emscripten" and self.settings.compiler == "clang":
            return "emscripten"
        elif self.settings.compiler == "gcc" and tools.is_apple_os(self.settings.os):
            return "darwin"
        elif self.settings.compiler == "apple-clang":
            return "clang"
        elif self.settings.os == "Android" and self.settings.compiler == "clang":
            return "clang-linux"
        elif self.settings.compiler in ["clang", "gcc"]:
            return str(self.settings.compiler)
        elif self.settings.compiler == "sun-cc":
            return "sunpro"
        elif self.settings.compiler == "intel":
            return {
                "Macos": "intel-darwin",
                "Windows": "intel-win",
                "Linux": "intel-linux",
            }[str(self.settings.os)]
        else:
            return str(self.settings.compiler)

    def test(self):
        tools.save(
            "jamroot.jam",
            'ECHO "info:" Success loading project jamroot.jam file. ;')
        self.run("b2 --debug-configuration toolset=%s" % self._toolset, run_environment=True)
