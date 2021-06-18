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
    exports_sources = ["patches/**"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _libname(self):
        return "liquid"

    @property
    def _target_name(self):
        if self.settings.os == "Macos":
            if not self.options.shared:
                return "libliquid.ar"
            return "libliquid.dylib"
        if not self.options.shared:
            return "libliquid.a"
        return "libliquid.so"

    @property
    def _lib_pattern(self):
        if self.settings.os == "Macos" and not self.options.shared:
            return "libliquid.a"
        if self.settings.os != "Windows":
            return self._target_name
        return "libliquid.lib"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os != "Windows":
            if not self.options.fPIC:
                raise ConanInvalidConfiguration("This library hardcodes fPIC")
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("VS is not supported")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("liquid-dsp-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=tools.os_info.is_windows
        )

        with tools.environment_append(self._autotools.vars):
            with tools.chdir(self._source_subfolder):
                self.run("./bootstrap.sh", win_bash=tools.os_info.is_windows)

        configure_args = []

        if self.settings.build_type == "Debug":
            configure_args.append("--enable-debug-messages")

        with tools.chdir(self._source_subfolder):
            self._autotools.configure(
                args=configure_args,
                configure_dir=os.path.join(self.source_folder, self._source_subfolder),
            )

        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        with tools.chdir(self._source_subfolder):
            autotools.make(target=self._target_name)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(
            pattern="liquid.h",
            dst="include/liquid",
            src=os.path.join(self._source_subfolder, "include"),
        )
        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Windows" and self.options.shared:
                os.rename("libliquid.so", "libliquid.dll")
                self.copy(pattern="libliquid.dll", dst="bin")
            elif self.settings.os == "Windows" and not self.options.shared:
                os.rename("libliquid.a", "libliquid.lib")
            elif self.settings.os == "Macos" and not self.options.shared:
                os.rename("libliquid.ar", "libliquid.a")
        self.copy(pattern=self._lib_pattern, dst="lib", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
