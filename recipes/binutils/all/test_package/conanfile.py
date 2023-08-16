from conan import ConanFile
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _has_as(self):
        return self._settings_build.os not in ("Macos",)

    @property
    def _has_ld(self):
        return self._settings_build.os not in ("Macos",)

    def layout(self):
        basic_layout(self)

    def test(self):
        binaries = ["ar", "nm", "objcopy", "objdump", "ranlib", "readelf", "strip"]
        if self._has_as:
            binaries.append("as")
        if self._has_ld:
            binaries.append("ld")

        for binary in binaries:
            self.run(f"{binary} --version", env="conanbuild")
