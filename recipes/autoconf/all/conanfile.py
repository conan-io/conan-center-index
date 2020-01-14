import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools


class AutoconfConan(ConanFile):
    name = "autoconf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf/"
    description = "Autoconf is an extensible package of M4 macros that produce shell scripts to automatically configure software source code packages"
    topics = ("conan", "autoconf", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os_build", "arch_build"
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build_requirements(self):
        if self.settings.os_build == "Windows" and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--datarootdir={}".format(os.path.join(self.package_folder, "bin", "share").replace("\\", "/")),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "info"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        autoconf = os.path.join(self.package_folder, "bin", "autoconf")
        self.output.info("Setting AUTOCONF to {}".format(autoconf))
        self.env_info.AUTOCONF = autoconf

        autoheader = os.path.join(self.package_folder, "bin", "autoheader")
        self.output.info("Setting AUTOHEADER to {}".format(autoheader))
        self.env_info.AUTOHEADER = autoheader

        autom4te = os.path.join(self.package_folder, "bin", "autom4te")
        self.output.info("Setting AUTOM4TE to {}".format(autom4te))
        self.env_info.AUTOM4TE = autom4te
