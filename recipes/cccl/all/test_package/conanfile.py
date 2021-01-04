from conans import ConanFile, tools
import os


class CcclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def build(self):
        environment = {}
        if self.settings.compiler == "Visual Studio":
            environment.update(tools.vcvars_dict(self.settings))
        with tools.environment_append(environment):
            cxx = tools.get_env("CXX")
            self.run("{cxx} {src} -o example".format(
                cxx=cxx, src=os.path.join(self.source_folder, "example.cpp")), win_bash=self.settings.os is "Windows")

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join(self.build_folder, "example"))
