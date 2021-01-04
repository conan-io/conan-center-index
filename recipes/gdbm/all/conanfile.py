from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class GdbmConan(ConanFile):
    name = "gdbm"
    description = ("gdbm is a library of database functions that uses "
                   "extensible hashing and work similar to "
                   "the standard UNIX dbm. "
                   "These routines are provided to a programmer needing "
                   "to create and manipulate a hashed database.")
    topics = ("conan", "gdbm", "dbm", "hash", "database")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org.ua/software/gdbm/gdbm.html"
    license = "GPL-3.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "libgdbm_compat": [True, False],
        "gdbmtool_debug": [True, False],
        "with_libiconv": [True, False],
        "with_readline": [True, False],
        "with_nls": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "libgdbm_compat": False,
        "gdbmtool_debug": True,
        "with_libiconv": False,
        "with_readline": False,
        "with_nls": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("gdbm is not supported on Windows")

    def configure(self):
        # Disabling NLS will render the dependency on libiconv and gettext moot
        # as the configure script will no longer look for that
        if not self.options.with_nls:
            if self.options.with_libiconv:
                raise ConanInvalidConfiguration(
                    "with_libiconv=True when with_nls=False is not possible "
                    "as it's NLS that requires libiconv")

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_libiconv:
            self.requires("libiconv/1.16")
        if self.options.with_readline:
            self.requires("readline/8.0")

    def build_requirements(self):
        self.build_requires("bison/3.5.3")
        self.build_requires("flex/2.6.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("gdbm-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        conf_args = [
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
            "--with-readline" if self.options.with_readline else "--without-readline",
            "--enable-libgdbm-compat" if self.options.libgdbm_compat else "--disable-libgdbm-compat",
            "--enable-gdbmtool-debug" if self.options.gdbmtool_debug else "--disable-gdbmtool-debug",
            "--disable-rpath",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend([
                "--disable-shared", "--enable-static",
                "--with-pic" if self.options.fPIC else "--without-pic"]
            )

        if not self.options.with_nls:
            conf_args.extend(["--disable-nls"])

        if self.options.with_libiconv:
            conf_args.extend([
                "--with-libiconv-prefix={}"
                .format(self.deps_cpp_info["libiconv"].rootpath),
                "--with-libintl-prefix"
            ])
        else:
            conf_args.extend(['--without-libiconv-prefix',
                              "--without-libintl-prefix"])

        self._autotools.configure(args=conf_args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            with tools.chdir("src"):
                autotools.make(target="maintainer-clean-generic")
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        os.unlink(os.path.join(self.package_folder, "lib", "libgdbm.la"))
        compat_la = os.path.join(self.package_folder, "lib",
                                 "libgdbm_compat.la")
        if (os.path.exists(compat_la)):
            os.unlink(compat_la)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.options.libgdbm_compat:
            self.cpp_info.libs.append("gdbm_compat")
        self.cpp_info.libs.append("gdbm")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
