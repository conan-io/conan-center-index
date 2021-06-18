from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import glob
import copy


class LiquidDspConan(ConanFile):
    name = "liquid-dsp"
    description = "Digital signal processing library for software-defined radios "
    topics = ("conan", "dsp", "sdr", "liquid-dsp")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jgaeddert/liquid-dsp"
    license = ("MIT",)
    settings = "os", "arch", "build_type", "compiler"
    exports_sources = ["generate_link_library.bat", "patches/**"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simdoverride": [True, False],
        "withfftw": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simdoverride": False,
        "withfftw": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _libname(self):
        if self.settings.os == "Windows":
            return "libliquid"
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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.withfftw:
            self.requires("fftw/3.3.9")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("mingw-w64/8.1")
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("liquid-dsp-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        have_to_rollback = False
        if self.settings.compiler == "Visual Studio":
            # Save current information
            old_compiler = str(self.settings.compiler)
            old_compiler_runtime = str(self.settings.compiler.runtime)
            old_compiler_toolset = str(self.settings.compiler.toolset)

            self.settings.compiler = "gcc"
            self.settings.compiler.version = "8.1"
            self.settings.compiler.threads = "win32"

            have_to_rollback = True

        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=tools.os_info.is_windows
        )

        with tools.environment_append(self._autotools.vars):
            with tools.chdir(self._source_subfolder):
                self.run("./bootstrap.sh", win_bash=tools.os_info.is_windows)

        configure_args = []

        if self.settings.build_type == "Debug":
            configure_args.append("--enable-debug-messages")
        if self.options.simdoverride:
            configure_args.append("--enable-simdoverride")

        with tools.chdir(self._source_subfolder):
            self._autotools.configure(
                args=configure_args,
                configure_dir=os.path.join(self.source_folder, self._source_subfolder),
            )

        # Restore old settings
        if have_to_rollback:
            self.settings.compiler = old_compiler
            self.settings.compiler.runtime = old_compiler_runtime
            self.settings.compiler.toolset = old_compiler_toolset
            del self.settings.compiler.cppstd

        return self._autotools

    def _patch_sources(self):
        if self.settings.os == "Windows":
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def _gen_link_library(self):
        if self.settings.compiler != "Visual Studio":
            return
        self.run("generate_link_library.bat")
        with tools.chdir(self._source_subfolder):
            self.run(
                """lib /def:libliquid.def /out:libliquid.lib """
                f"""/machine:{"X86" if self.settings.arch=="x86" else "X64"}""",
                win_bash=tools.os_info.is_windows,
            )

    def _rename_libraries(self):
        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Windows" and self.options.shared:
                os.rename("libliquid.so", "libliquid.dll")
            elif self.settings.os == "Windows" and not self.options.shared:
                os.rename("libliquid.a", "libliquid.lib")
            elif self.settings.os == "Macos" and not self.options.shared:
                os.rename("libliquid.ar", "libliquid.a")

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        with tools.chdir(self._source_subfolder):
            autotools.make(target=self._target_name)
        self._rename_libraries()
        self._gen_link_library()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(
            pattern="liquid.h",
            dst="include/liquid",
            src=os.path.join(self._source_subfolder, "include"),
        )
        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Windows" and self.options.shared:
                self.copy(pattern="libliquid.dll", dst="bin")
        self.copy(pattern=self._lib_pattern, dst="lib", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
