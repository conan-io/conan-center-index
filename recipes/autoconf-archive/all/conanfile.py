import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


required_conan_version = ">=1.33.0"

class AutoconfArchiveConan(ConanFile):
    name = "autoconf-archive"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf-archive/"
    license = "GPL-2.0-or-later"
    description = "The GNU Autoconf Archive is a collection of more than 500 macros for GNU Autoconf"
    topics = ("conan", "GNU", "autoconf", "autoconf-archive", "macro")
    settings = "os"
    _source_subfolder = "source_subfolder"
    _autotools = None

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("only Linux is supported")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_name = "autoconf-archive-" + self.version
        tools.rename(extracted_name, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
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

    def package_info(self):
        aclocal_path = os.path.join(self.package_folder, "share", "aclocal")
        self.output.info("Appending ACLOCAL_PATH environment var: {}".format(aclocal_path))
        self.env_info.ACLOCAL_PATH.append(aclocal_path)
