from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class AutomakeConan(ConanFile):
    name = "automake"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    description = "Automake is a tool for automatically generating Makefile.in files compliant with the GNU Coding Standards."
    topics = ("conan", "automake", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"

    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @property
    def _version_major_minor(self):
        [major, minor, _] = self.version.split(".", 2)
        return '{}.{}'.format(major, minor)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("autoconf/2.71")
        # automake requires perl-Thread-Queue package

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires("autoconf/2.71")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    @property
    def _automake_libdir(self):
        return os.path.join(self._datarootdir, "automake-{}".format(self._version_major_minor))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--datarootdir={}".format(tools.unix_path(self._datarootdir)),
            "--prefix={}".format(tools.unix_path(self.package_folder)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_files(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.os == "Windows":
            # tracing using m4 on Windows returns Windows paths => use cygpath to convert to unix paths
            tools.replace_in_file(os.path.join(self._source_subfolder, "bin", "aclocal.in"),
                                               "          $map_traced_defs{$arg1} = $file;",
                                               "          $file = `cygpath -u $file`;\n"
                                               "          $file =~ s/^\\s+|\\s+$//g;\n"
                                               "          $map_traced_defs{$arg1} = $file;")

    def build(self):
        self._patch_files()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self._datarootdir, "info"))
        tools.files.rmdir(self, os.path.join(self._datarootdir, "man"))
        tools.files.rmdir(self, os.path.join(self._datarootdir, "doc"))

        if self.settings.os == "Windows":
            binpath = os.path.join(self.package_folder, "bin")
            for filename in os.listdir(binpath):
                fullpath = os.path.join(binpath, filename)
                if not os.path.isfile(fullpath):
                    continue
                os.rename(fullpath, fullpath + ".exe")

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable:: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""

        aclocal = tools.unix_path(os.path.join(self.package_folder, "bin", "aclocal" + bin_ext))
        self.output.info("Appending ACLOCAL environment variable with: {}".format(aclocal))
        self.env_info.ACLOCAL.append(aclocal)

        automake_datadir = tools.unix_path(self._datarootdir)
        self.output.info("Setting AUTOMAKE_DATADIR to {}".format(automake_datadir))
        self.env_info.AUTOMAKE_DATADIR = automake_datadir

        automake_libdir = tools.unix_path(self._automake_libdir)
        self.output.info("Setting AUTOMAKE_LIBDIR to {}".format(automake_libdir))
        self.env_info.AUTOMAKE_LIBDIR = automake_libdir

        automake_perllibdir = tools.unix_path(self._automake_libdir)
        self.output.info("Setting AUTOMAKE_PERLLIBDIR to {}".format(automake_perllibdir))
        self.env_info.AUTOMAKE_PERLLIBDIR = automake_perllibdir

        automake = tools.unix_path(os.path.join(self.package_folder, "bin", "automake" + bin_ext))
        self.output.info("Setting AUTOMAKE to {}".format(automake))
        self.env_info.AUTOMAKE = automake

        self.output.info("Append M4 include directories to AUTOMAKE_CONAN_INCLUDES environment variable")

        self.user_info.compile = os.path.join(self._automake_libdir, "compile")
        self.user_info.ar_lib = os.path.join(self._automake_libdir, "ar-lib")
