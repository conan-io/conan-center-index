from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException
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
        if self.settings.os != "Windows":
            return "liquid"
        return "libliquid"

    @property
    def _target_name(self):
        if self.settings.os == "Macos":
            if not self.options.shared:
                return "libliquid.ar"
            return "libliquid.dylib"
        if not self.options.shared:
            return "libliquid.a"
        return "libliquid.so"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("liquid-dsp-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                    "AR": "{} lib".format(
                        tools.unix_path(self.deps_user_info["automake"].ar_lib)
                    ),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

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

        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")

        with tools.chdir(self._source_subfolder):
            self._autotools.configure(
                args=configure_args,
                configure_dir=os.path.join(self.source_folder, self._source_subfolder),
            )

        return self._autotools

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
            # Make the files be MSVC friendly
            for subdir, dirs, files in os.walk(
                os.path.join(self.source_folder, self._source_subfolder)
            ):
                for file in files:
                    filepath = os.path.join(
                        self.source_folder, self._source_subfolder, subdir, file
                    )
                    try:
                        tools.replace_in_file(filepath, "float complex", "_Fcomplex")
                        tools.replace_in_file(filepath, "double complex", "_Dcomplex")
                    except ConanException:  # ConanException: replace_in_file didn't find pattern
                        continue

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            with tools.chdir(self._source_subfolder):
                autotools.make(target=self._target_name)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
