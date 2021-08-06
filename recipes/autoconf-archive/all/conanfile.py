from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"


class AutoconfArchiveConan(ConanFile):
    name = "autoconf-archive"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf-archive/"
    license = "GPL-2.0-or-later"
    description = "The GNU Autoconf Archive is a collection of more than 500 macros for GNU Autoconf"
    topics = ("conan", "GNU", "autoconf", "autoconf-archive", "macro")
    settings = "os"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
            self._autotools.configure()
        return self._autotools

    def build(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            self._autotools = self._configure_autotools()
            self._autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.chdir(os.path.join(self._source_subfolder)):
            self._autotools = self._configure_autotools()
            self._autotools.install()

        tools.mkdir(os.path.join(self.package_folder, "res"))
        tools.rename(os.path.join(self.package_folder, "share", "aclocal"),
                     os.path.join(self.package_folder, "res", "aclocal"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        aclocal_path = tools.unix_path(os.path.join(self.package_folder, "res", "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment var: {}".format(aclocal_path))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal_path)
