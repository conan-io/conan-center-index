from functools import lru_cache
from os import environ, path

from conan import ConanFile
from conan.tools.files import get, apply_conandata_patches, rmdir, copy, replace_in_file
from conan.tools.gnu import Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class AutomakeConan(ConanFile):
    name = "automake"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    description = "Automake is a tool for automatically generating Makefile.in files compliant with the GNU Coding Standards."
    topics = ("conan", "automake", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os", "arch", "compiler", "build_type"
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualBuildEnv"
    win_bash = True

    exports_sources = "patches/*"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.tool_requires("autoconf/2.71")
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def layout(self):
        basic_layout(self, src_folder="source")
        self.cpp.package.includedirs = []  # KB-H071: It is a tool that doesn't contain headers, removing the include directory.

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _datarootdir(self):
        return path.join(self.package_folder, "bin", "share")

    @property
    def _automake_libdir(self):
        version = Version(self.version)
        return path.join(self._datarootdir, f"automake-{version.major}.{version.minor}")

    @lru_cache(1)
    def _autotools(self):
        autotool = Autotools(self)
        autotool.configure()
        autotool.make()
        return autotool

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            # tracing using m4 on Windows returns Windows paths => use cygpath to convert to unix paths
            replace_in_file(self, path.join(self.source_path, "bin", "aclocal.in"),
                            "          $map_traced_defs{$arg1} = $file;",
                            "          $file = `cygpath -u $file`;\n"
                            "          $file =~ s/^\\s+|\\s+$//g;\n"
                            "          $map_traced_defs{$arg1} = $file;")

        _ = self._autotools()

    def package(self):
        autotools = self._autotools()
        # KB-H013 we're packaging an application, place everything under bin
        autotools.install(args=[f"DESTDIR={unix_path(self, path.join(self.package_folder, 'bin'))}"])

        copy(self, "COPYING*", src=self.source_folder, dst=path.join(self.package_folder, "licenses"))
        rmdir(self, path.join(self._datarootdir, "info"))
        rmdir(self, path.join(self._datarootdir, "man"))
        rmdir(self, path.join(self._datarootdir, "doc"))

    def _set_env(self, var_name, var_path):
        self.output.info(f"Setting {var_name} to {var_path}")
        if path.isfile(var_path):
            self.buildenv_info.define(var_name, var_path)
        else:
            self.buildenv_info.define_path(var_name, var_path)
        setattr(self.env_info, var_name,  self, var_path)

    def package_info(self):
        # KB-H013 we're packaging an application, hence the nested bin
        bin_dir = path.join(self.package_folder, "bin", "bin")
        self.output.info(f"Appending PATH environment variable:: {bin_dir}")
        self.buildenv_info.prepend_path("PATH", bin_dir)
        self.env_info.PATH.append(bin_dir)

        for var in [("ACLOCAL", path.join(self.package_folder, "bin", "aclocal")),
                    ("AUTOMAKE_DATADIR", self._datarootdir),
                    ("AUTOMAKE_LIBDIR", self._automake_libdir),
                    ("AUTOMAKE_PERLLIBDIR", self._automake_libdir),
                    ("AUTOMAKE", path.join(self.package_folder, "bin", "automake"))]:
            self._set_env(*var)

        compile_bin = path.join(self._automake_libdir, "compile")
        self.output.info(f"Define path to `compile` binary in user_info as: {compile_bin}")
        self.user_info.compile = compile_bin
        compile_conf_key = "user.automake:compile"
        self.output.info(f"Defining path to `compile` binary in configuration as `{compile_conf_key}` with value: {compile_bin}")
        self.conf_info.define(compile_conf_key, compile_bin)

        ar_lib_bin = path.join(self._automake_libdir, "ar-lib")
        self.output.info(f"Define path to `ar_lib` binary in user_info as: {ar_lib_bin}")
        self.user_info.ar_lib = ar_lib_bin
        ar_lib_conf_key = "user.automake:ar-lib"
        self.output.info(f"Defining path to `ar-lib` binary in configuration as `{ar_lib_conf_key}` with value: {ar_lib_bin}")
        self.conf_info.define(ar_lib_conf_key, ar_lib_bin)
