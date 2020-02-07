import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager


class LibtoolConan(ConanFile):
    name = "libtool"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libtool/"
    description = "GNU libtool is a generic library support script. "
    topics = ("conan", "libtool", "configure", "library", "shared", "static")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")

    settings = "os_build", "arch_build", "compiler"
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def config_options(self):
        # libtool provides a ltdl library, which is not packaged by this recipe
        # To make the hooks happy, remove the c++ related settings
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def requirements(self):
        self.requires("automake/1.16.1")

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        datarootdir = os.path.join(self.package_folder, "bin", "share")
        prefix = self.package_folder
        if self.settings.os_build == "Windows":
            datarootdir = tools.unix_path(datarootdir)
            prefix = tools.unix_path(prefix)
        conf_args = [
            "--datarootdir={}".format(datarootdir),
            "--prefix={}".format(prefix),
            "--disable-shared",
            "--disable-static",
            "--disable-ltdl-install",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "info"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))

        if self.settings.os_build == "Windows":
            binpath = os.path.join(self.package_folder, "bin")
            for filename in os.listdir(binpath):
                fullpath = os.path.join(binpath, filename)
                if not os.path.isfile(fullpath):
                    continue
                os.rename(fullpath, fullpath + ".exe")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os_build == "Windows" else ""

        libtool = os.path.join(self.package_folder, "bin", "libtool" + bin_ext)
        if self.settings.os_build == "Windows":
            libtool = tools.unix_path(libtool)
        self.output.info("Setting LIBTOOL to {}".format(libtool))
        self.env_info.LIBTOOL = libtool

        libtoolize = os.path.join(self.package_folder, "bin", "libtoolize" + bin_ext)
        if self.settings.os_build == "Windows":
            libtoolize = tools.unix_path(libtoolize)
        self.output.info("Setting LIBTOOLIZE to {}".format(libtoolize))
        self.env_info.LIBTOOLIZE = libtoolize

        libtool_aclocal = os.path.join(self.package_folder, "bin", "share", "aclocal" + bin_ext)
        if self.settings.os_build == "Windows":
            libtool_aclocal = tools.unix_path(libtool_aclocal)
        self.output.info("Appending var to ACLOCAL_PATH: {}".format(libtool_aclocal))
        self.env_info.ACLOCAL_PATH.append(libtool_aclocal)
