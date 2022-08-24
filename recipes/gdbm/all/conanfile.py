from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


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

    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self.options.with_nls:
            del self.options.with_libiconv

    def requirements(self):
        if self.options.get_safe("with_libiconv"):
            self.requires("libiconv/1.16")
        if self.options.with_readline:
            self.requires("readline/8.1.2")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("gdbm is not supported on Windows")

    def build_requirements(self):
        self.build_requires("bison/3.7.6")
        self.build_requires("flex/2.6.4")
        self.build_requires("gnu-config/cci.20210814")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", None) or self.deps_user_info

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "build-aux", "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "build-aux", "config.guess"))

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
                "--with-pic" if self.options.get_safe("fPIC", True) else "--without-pic"]
            )

        if not self.options.with_nls:
            conf_args.extend(["--disable-nls"])

        if self.options.get_safe("with_libiconv"):
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
        self._patch_sources()
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
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.options.libgdbm_compat:
            self.cpp_info.libs.append("gdbm_compat")
        self.cpp_info.libs.append("gdbm")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
