from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import contextlib
import os

required_conan_version = ">=1.33.0"


class XorgCfFilesConan(ConanFile):
    name = "xorg-cf-files"
    description = "Imake configuration files & templates"
    topics = ("conan", "imake", "xorg", "template", "configuration", "obsolete")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/cf"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"

    exports_sources = "patches/*"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("xorg-macros/1.19.3")
        self.requires("xorg-proto/2021.4")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if tools.is_apple_os(self, self.settings.os):
            raise ConanInvalidConfiguration("This recipe does not support Apple operating systems.")

    def package_id(self):
        del self.info.settings.compiler
        # self.info.settings.os  # FIXME: can be removed once c3i is able to test multiple os'es from one common package

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "CPP": "{} cl -E".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []

        self.user_info.CONFIG_PATH = os.path.join(self.package_folder, "lib", "X11", "config").replace("\\", "/")
