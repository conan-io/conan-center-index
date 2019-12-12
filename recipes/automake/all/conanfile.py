import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools


class AutomakeConan(ConanFile):
    name = "automake"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    description = "Automake is a tool for automatically generating Makefile.in files compliant with the GNU Coding Standards."
    topics = ("conan", "automake", "configure", "build")
    exports_sources = ["patches/**"]
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")

    settings = "os_build", "arch_build"
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def requirements(self):
        self.requires("autoconf/2.69")
        # automake requires perl-Thread-Queue package

    def build_requirements(self):
        if self.settings.os_build == "Windows" and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        datarootdir = os.path.join(self.package_folder, "bin", "share")
        prefix = self.package_folder
        if tools.os_info.is_windows:
            datarootdir = tools.unix_path(datarootdir)
            prefix = tools.unix_path(prefix)
        conf_args = [
            "--datarootdir={}".format(datarootdir),
            "--prefix={}".format(prefix),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_files(self):
        for patch in self.conan_data["patches"][self.version]:
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
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "doc"))

        if self.settings.os_build == "Windows":
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

        aclocal = os.path.join(self.package_folder, "bin", "aclocal")
        if self.settings.os_build == "Windows":
            aclocal = tools.unix_path(aclocal) + ".exe"
        self.output.info("Setting ACLOCAL to {}".format(aclocal))
        self.env_info.ACLOCAL = aclocal

        automake = os.path.join(self.package_folder, "bin", "automake")
        if self.settings.os_build == "Windows":
            automake = tools.unix_path(automake) + ".exe"
        self.output.info("Setting AUTOMAKE to {}".format(automake))
        self.env_info.AUTOMAKE = automake
