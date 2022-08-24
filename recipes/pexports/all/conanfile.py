from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import os

required_conan_version = ">=1.33.0"


class PExportsConan(ConanFile):
    name = "pexports"
    description = "pexports is a program to extract exported symbols from a PE image (executable)."
    homepage = "https://sourceforge.net/projects/mingw/files/MinGW/Extension/pexports/"
    license = "GPL-2.0-or-later"
    topics = ("windows", "dll", "PE", "symbols", "import", "library")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        self.build_requires("automake/1.16.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        filename = "pexports.tar.xz"
        tools.files.get(self, **self.conan_data["sources"][self.version], filename=filename,
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        host = build = None
        if self.settings.compiler == "Visual Studio":
            self._autotools.defines.append("YY_NO_UNISTD_H")
            host = build = False
        self._autotools.configure(configure_dir=self._source_subfolder, host=host, build=build)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
