from functools import lru_cache
from os import environ, path

from conan import ConanFile
from conan.tools.files import get, apply_conandata_patches, rmdir
from conan.tools.gnu import Autotools
from conan.tools.microsoft import unix_path
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"


class AutoconfConan(ConanFile):
    name = "autoconf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf/"
    description = "Autoconf is an extensible package of M4 macros that produce shell scripts to automatically configure software source code packages"
    topics = ("autoconf", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os", "arch", "compiler", "build_type"
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualBuildEnv"
    win_bash = True

    exports_sources = "patches/*"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _datarootdir(self):
        return path.join(self.package_folder, "bin", "share")

    @property
    def _autoconf_datarootdir(self):
        return path.join(self._datarootdir, "autoconf")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("m4/1.4.19")

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.tool_requires("m4/1.4.19")
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self, src_folder="source")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @lru_cache(1)
    def _autotools(self):
        autotool = Autotools(self)
        autotool.configure()
        autotool.make()
        return autotool

    def build(self):
        apply_conandata_patches(self)
        self._autotools()

    def package(self):
        autotools = self._autotools()
        # KB-H013 we're packaging an application, place everything under bin
        autotools.install(args=[f"DESTDIR={unix_path(self, path.join(self.package_folder, 'bin'))}"])
        rmdir(self, path.join(self._datarootdir, "info"))
        rmdir(self, path.join(self._datarootdir, "man"))

    def _set_env(self, var_name, var_path):
        self.output.info(f"Setting {var_name} to {var_path}")
        self.buildenv_info.define_path(var_name, var_path)
        setattr(self.env_info, var_name, unix_path(self, var_path))

    def package_info(self):
        # KB-H013 we're packaging an application, hence the nested bin
        bin_dir = path.join(self.package_folder, "bin", "bin")
        self.output.info(f"Appending PATH env var with : {bin_dir}")
        self.buildenv_info.prepend_path("PATH", bin_dir)
        self.env_info.PATH.append(unix_path(self, bin_dir))

        for var in [("AC_MACRODIR", self._autoconf_datarootdir),
                    ("AUTOCONF", path.join(bin_dir, "autoconf")),
                    ("AUTORECONF", path.join(bin_dir, "autoreconf")),
                    ("AUTOHEADER", path.join(bin_dir, "autoheader")),
                    ("AUTOM4TE", path.join(bin_dir, "autom4te")),
                    ("AUTOM4TE_PERLLIBDIR", self._autoconf_datarootdir)]:
            self._set_env(*var)
