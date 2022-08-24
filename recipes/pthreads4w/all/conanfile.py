from conans import AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class Pthreads4WConan(ConanFile):
    name = "pthreads4w"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/pthreads4w/"
    description = "POSIX Threads for Windows"
    license = "Apache-2.0"
    topics = ("pthreads", "windows", "posix")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "exception_scheme": ["CPP", "SEH", "default"],
    }
    default_options = {
        "shared": False,
        "exception_scheme": "default",
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("autoconf/2.71")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("pthreads4w can only target os=Windows")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure()
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            if self.settings.compiler == "Visual Studio":
                tools.replace_in_file("Makefile",
                    "	copy pthreadV*.lib $(LIBDEST)",
                    "	if exist pthreadV*.lib copy pthreadV*.lib $(LIBDEST)")
                tools.replace_in_file("Makefile",
                    "	copy libpthreadV*.lib $(LIBDEST)",
                    "	if exist libpthreadV*.lib copy libpthreadV*.lib $(LIBDEST)")
                tools.replace_in_file("Makefile", "XCFLAGS=\"/MD\"", "")
                tools.replace_in_file("Makefile", "XCFLAGS=\"/MDd\"", "")
                tools.replace_in_file("Makefile", "XCFLAGS=\"/MT\"", "")
                tools.replace_in_file("Makefile", "XCFLAGS=\"/MTd\"", "")
                target = {
                    "CPP": "VCE",
                    "SEH": "SSE",
                }.get(str(self.options.exception_scheme), "VC")
                if not self.options.shared:
                    target += "-static"
                if self.settings.build_type == "Debug":
                    target += "-debug"
                with tools.vcvars(self):
                    with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                        self.run("nmake {}".format(target))
            else:
                self.run("{}".format(tools.get_env("AUTOHEADER")), win_bash=tools.os_info.is_windows)
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)

                autotools = self._configure_autotools()

                make_target = "GCE" if self.options.exception_scheme == "CPP" else "GC"
                if not self.options.shared:
                    make_target += "-static"
                if self.settings.build_type == "Debug":
                    make_target += "-debug"
                autotools.make(target=make_target, args=["-j1"])

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self):
                    with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                        self.run("nmake install DESTROOT={}".format(self.package_folder))
            else:
                autotools = self._configure_autotools()
                tools.mkdir(os.path.join(self.package_folder, "include"))
                tools.mkdir(os.path.join(self.package_folder, "lib"))
                autotools.make(target="install-headers")
                if self.options.shared:
                    tools.mkdir(os.path.join(self.package_folder, "bin"))
                    autotools.make(target="install-dlls")
                    autotools.make(target="install-implib-default")
                else:
                    autotools.make(target="install-lib-default")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append(self._exception_scheme_definition)
        if not self.options.shared:
            self.cpp_info.defines.append("__PTW32_STATIC_LIB")

    @property
    def _exception_scheme_definition(self):
        return {
            "CPP": "__PTW32_CLEANUP_CXX",
            "SEH": "__PTW32_CLEANUP_SEH",
            "default": "__PTW32_CLEANUP_C",
        }[str(self.options.exception_scheme)]
