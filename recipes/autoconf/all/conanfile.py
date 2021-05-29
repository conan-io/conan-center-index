import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools


class AutoconfConan(ConanFile):
    name = "autoconf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf/"
    description = "Autoconf is an extensible package of M4 macros that produce shell scripts to automatically configure software source code packages"
    topics = ("conan", "autoconf", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    exports_sources = "patches/**"
    settings = "os", "arch", "compiler"
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def requirements(self):
        self.requires("m4/1.4.18")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        # The m4 requirement does not change the contents of this package
        self.info.requires.clear()

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    @property
    def _autoconf_datarootdir(self):
        return os.path.join(self._datarootdir, "autoconf")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        datarootdir = self._datarootdir
        prefix = self.package_folder
        if self.settings.os == "Windows":
            datarootdir = tools.unix_path(datarootdir)
            prefix = tools.unix_path(prefix)
        conf_args = [
            "--datarootdir={}".format(datarootdir),
            "--prefix={}".format(prefix),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_files(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_files()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "info"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))

        if self.settings.os == "Windows":
            binpath = os.path.join(self.package_folder, "bin")
            for filename in os.listdir(binpath):
                fullpath = os.path.join(binpath, filename)
                if not os.path.isfile(fullpath):
                    continue
                os.rename(fullpath, fullpath + ".exe")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        ac_macrodir = self._autoconf_datarootdir
        self.output.info("Setting AC_MACRODIR to {}".format(ac_macrodir))
        self.env_info.AC_MACRODIR = ac_macrodir

        autoconf = os.path.join(self.package_folder, "bin", "autoconf")
        if self.settings.os == "Windows":
            autoconf = tools.unix_path(autoconf) + ".exe"
        self.output.info("Setting AUTOCONF to {}".format(autoconf))
        self.env_info.AUTOCONF = autoconf

        autoreconf = os.path.join(self.package_folder, "bin", "autoreconf")
        if self.settings.os == "Windows":
            autoreconf = tools.unix_path(autoreconf) + ".exe"
        self.output.info("Setting AUTORECONF to {}".format(autoreconf))
        self.env_info.AUTORECONF = autoreconf

        autoheader = os.path.join(self.package_folder, "bin", "autoheader")
        if self.settings.os == "Windows":
            autoheader = tools.unix_path(autoheader) + ".exe"
        self.output.info("Setting AUTOHEADER to {}".format(autoheader))
        self.env_info.AUTOHEADER = autoheader

        autom4te = os.path.join(self.package_folder, "bin", "autom4te")
        if self.settings.os == "Windows":
            autom4te = tools.unix_path(autom4te) + ".exe"
        self.output.info("Setting AUTOM4TE to {}".format(autom4te))
        self.env_info.AUTOM4TE = autom4te

        autom4te_perllibdir = self._autoconf_datarootdir
        self.output.info("Setting AUTOM4TE_PERLLIBDIR to {}".format(autom4te_perllibdir))
        self.env_info.AUTOM4TE_PERLLIBDIR = autom4te_perllibdir
