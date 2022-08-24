from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class GperfConan(ConanFile):
    name = "gperf"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gperf"
    description = "GNU gperf is a perfect hash function generator"
    topics = ("gperf", "hash-generator", "hash")

    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def package_id(self):
        del self.info.settings.compiler

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._is_msvc:
            self.build_requires("automake/1.16.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            if self._is_msvc and tools.scm.Version(self.settings.compiler.version) >= "12":
                self._autotools.flags.append("-FS")
            self._autotools.configure()
        return self._autotools

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextmanager
    def _build_context(self):
        with tools.files.chdir(self, self._source_subfolder):
            if self._is_msvc:
                with tools.vcvars(self.settings):
                    env = {
                        "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                        "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                        "CFLAGS": "-{}".format(self.settings.compiler.runtime),
                        "CXXLAGS": "-{}".format(self.settings.compiler.runtime),
                        "CPPFLAGS": "-D_WIN32_WINNT=_WIN32_WINNT_WIN8",
                        "LD": "link",
                        "NM": "dumpbin -symbols",
                        "STRIP": ":",
                        "AR": "{} lib".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].ar_lib)),
                        "RANLIB": ":",
                    }
                    with tools.environment_append(env):
                        yield
            else:
                yield

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
