from io import StringIO

from conan import ConanFile, conan_version
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
    
    @property
    def _version(self):
        if conan_version.major >= 2:
            return self.dependencies.build["git"].ref.version
        else:
            return self.deps_cpp_info["git"].version

    def build(self):
        pass

    def test(self):
        if can_run(self):
            buffer = StringIO()
            self.run("git --version", buffer)
            self.output.info(buffer.getvalue())
            version_detected = buffer.getvalue().split()[-1].strip()
            # The string can either be literally the version, or '<version>.GIT'
            if str(self._version) not in version_detected:
                raise ConanException(
                    f"git reported wrong version. Expected {self._version}, got {version_detected}."
                )
