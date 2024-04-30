from io import StringIO

from conan import ConanFile, conan_version
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)
    
    @property
    def _version(self):
        if conan_version.major >= 2:
            return self.dependencies["git"].ref.version
        else:
            return self.deps_cpp_info["git"].version

    def build(self):
        pass

    def test(self):
        if can_run(self):
            buffer = StringIO()
            self.run("git --version", buffer, env="conanrun")
            self.output.info(buffer.getvalue())
            version_detected = buffer.getvalue().split()[-1].strip()
            if self._version != version_detected:
                raise ConanException(
                    f"git reported wrong version. Expected {self._version}, got {version_detected}."
                )
