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
        "simdoverride": [True, False],
    }
    default_options = {
        "shared": False,
        "simdoverride": False,
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

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("mingw-w64/8.1")
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True,
        )

    def _patch_sources(self):
        if self.settings.os == "Windows":
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def _gen_link_library(self):
        if self.settings.compiler != "Visual Studio" or (not self.options.shared):
            return
        self.run("cmd /c generate_link_library.bat")
        with tools.chdir(self._source_subfolder):
            self.run(
                "{} /def:libliquid.def /out:libliquid.lib /machine:{}".format(
                    os.getenv("AR"), "X86" if self.settings.arch == "x86" else "X64"
                ),
                win_bash=tools.os_info.is_windows,
            )

    def _rename_libraries(self):
        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Windows" and self.options.shared:
                tools.rename("libliquid.so", "libliquid.dll")
            elif self.settings.os == "Windows" and not self.options.shared:
                os.rename("libliquid.a", "libliquid.lib")
            elif self.settings.os == "Macos" and not self.options.shared:
                os.rename("libliquid.ar", "libliquid.a")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            env = {
                "CC": "gcc",
                "CXX": "g++",
                "LD": "ld",
                "AR": "ar",
            }
            with tools.environment_append(env):
                yield
        else:
            yield

    @contextmanager
    def _msvc_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "AR": "lib",
                    "LD": "link",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        self._patch_sources()
        ncpus = os.cpu_count()
        ncpus = ncpus if ncpus else 1
        configure_args = []
        if self.settings.build_type == "Debug":
            configure_args.append("--enable-debug-messages")
        if self.options.simdoverride:
            configure_args.append("--enable-simdoverride")
        if self.settings.compiler == "Visual Studio":
            configure_args.append("CFLAGS='-static-libgcc'")
        configure_args_str = " ".join(configure_args)
        with self._build_context():
            with tools.chdir(self._source_subfolder):
                self.run("./bootstrap.sh", win_bash=tools.os_info.is_windows)
                self.run(
                    "./configure {}".format(configure_args_str),
                    win_bash=tools.os_info.is_windows,
                )
                self.run(
                    "make {} -j{}".format(self._target_name, ncpus),
                    win_bash=tools.os_info.is_windows,
                )
        self._rename_libraries()
        with self._msvc_context():
            self._gen_link_library()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(
            pattern="liquid.h",
            dst="include/liquid",
            src=os.path.join(self._source_subfolder, "include"),
        )
        self.copy(pattern="libliquid.dll", dst="bin", src=self._source_subfolder)
        self.copy(pattern=self._lib_pattern, dst="lib", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
