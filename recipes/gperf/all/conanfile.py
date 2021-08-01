from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"


class GperfConan(ConanFile):
    name = "gperf"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gperf"
    description = "GNU gperf is a perfect hash function generator"
    topics = ("conan", "gperf", "hash-generator", "hash")
    settings = "os", "arch", "compiler", "build_type"
    _source_subfolder = "source_subfolder"
    _autotools = None
    exports_sources = "patches/*"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw_windows(self):
        return self.settings.os == "Windows" and tools.os_info.is_windows and self.settings.compiler == "gcc"

    def package_id(self):
        del self.info.settings.compiler

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._autotools:
            args = []
            cwd = os.getcwd()
            win_bash = self._is_msvc or self._is_mingw_windows
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=win_bash)
            if self._is_msvc:
                args.extend(["CC={}/build-aux/compile cl -nologo".format(cwd),
                            "CFLAGS=-{}".format(self.settings.compiler.runtime),
                            "CXX={}/build-aux/compile cl -nologo".format(cwd),
                            "CXXFLAGS=-{}".format(self.settings.compiler.runtime),
                            "CPPFLAGS=-D_WIN32_WINNT=_WIN32_WINNT_WIN8",
                            "LD=link",
                            "NM=dumpbin -symbols",
                            "STRIP=:",
                            "AR={}/build-aux/ar-lib lib".format(cwd),
                            "RANLIB=:"])
            elif self.settings.compiler == "gcc" and self.settings.os == "Windows":
                self._autotools.link_flags.extend(["-static", "-static-libgcc"])

            self._autotools.configure(args=args)
        return self._autotools

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self._is_msvc:
            with tools.vcvars(self.settings):
                self._build_configure()
        else:
            self._build_configure()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
