from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import glob


class LiquidDspConan(ConanFile):
    name = "liquid-dsp"
    description = "Digital signal processing library for software-defined radios "
    topics = ("conan", "dsp", "sdr", "liquid-dsp")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jgaeddert/liquid-dsp"
    license = ("MIT",)
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx~

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("liquid-dsp-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=tools.os_info.is_windows)

        with tools.environment_append(self._autotools.vars):
            with tools.chdir(self._source_subfolder):
                self.run("./autogen.sh", win_bash=tools.os_info.is_windows)

        configure_args = [
            # "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
            # "--enable-static=%s" % ("no" if self.options.shared else "yes")
            # Eventually I'll have some
        ]

        self._autotools.configure(args=configure_args,
                                  configure_dir=self._source_subfolder)

        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = ["liquid-dsp"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
