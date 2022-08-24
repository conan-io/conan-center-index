from conan import ConanFile, tools$
import os


class CcclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def build(self):
        environment = {}
        if self.settings.compiler == "Visual Studio":
            environment.update(tools.vcvars_dict(self.settings))
        with tools.environment_append(environment):
            cxx = tools.get_env("CXX")
            self.run("{cxx} {src} -o example".format(
                cxx=cxx, src=os.path.join(self.source_folder, "example.cpp")), win_bash=self.settings.os is "Windows")

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(os.path.join(self.build_folder, "example"))
