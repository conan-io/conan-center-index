from os import path

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.52"


class AutomakeConan(ConanFile):
    name = "automake"
    description = "Automake is a tool for automatically generating Makefile.in files compliant with the GNU Coding Standards."
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    topics = ("conan", "automake", "configure", "build")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.win_bash = self._settings_build.os == "Windows"
        try:
            del self.settings.compiler.libcxx  # for plain C projects only
        except ValueError:
            pass
        try:
            del self.settings.compiler.cppstd  # for plain C projects only
        except ValueError:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("autoconf/2.71")
        self.requires("m4/1.4.19")

    def package_id(self):
        try:
            del self.info.settings.arch
        except ValueError:
            pass
        try:
            del self.info.settings.compiler
        except ValueError:
            pass
        try:
            del self.info.settings.build_type
        except ValueError:
            pass

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
        ])

        if is_msvc(self):
            build = "{}-{}-{}".format(
                "x86_64" if self._settings_build.arch == "x86_64" else "i686",
                "pc" if self._settings_build.arch == "x86" else "win64",
                "mingw32")
            host = "{}-{}-{}".format(
                "x86_64" if self.settings.arch == "x86_64" else "i686",
                "pc" if self.settings.arch == "x86" else "win64",
                "mingw32")
            tc.configure_args.append(f"--build={build}")
            tc.configure_args.append(f"--host={host}")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            # tracing using m4 on Windows returns Windows paths => use cygpath to convert to unix paths
            replace_in_file(self, path.join(self.source_folder, "bin", "aclocal.in"),
                            "          $map_traced_defs{$arg1} = $file;",
                            "          $file = `cygpath -u $file`;\n"
                            "          $file =~ s/^\\s+|\\s+$//g;\n"
                            "          $map_traced_defs{$arg1} = $file;")

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem

        copy(self, "COPYING*", src=self.source_folder, dst=path.join(self.package_folder, "licenses"))
        for sub_path in ("info", "man", "doc"):
            rmdir(self, path.join(self.package_folder, "res", sub_path))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        dataroot_path = path.join(self.package_folder, "res")
        self.output.info(f"Defining AUTOMAKE_DATADIR environment variable: {dataroot_path}")
        self.env_info.AUTOMAKE_DATADIR = dataroot_path
        self.buildenv_info.define_path("AUTOMAKE_DATADIR", dataroot_path)

        version = Version(self.version)
        automake_dataroot_path = path.join(dataroot_path, f"automake-{version.major}.{version.minor}")
        self.output.info(f"Defining AUTOMAKE_LIBDIR environment variable: {automake_dataroot_path}")
        self.env_info.AUTOMAKE_LIBDIR = automake_dataroot_path
        self.buildenv_info.define_path("AUTOMAKE_LIBDIR", automake_dataroot_path)

        self.output.info(f"Defining AUTOMAKE_PERLLIBDIR environment variable: {automake_dataroot_path}")
        self.env_info.AUTOMAKE_PERLLIBDIR = automake_dataroot_path
        self.buildenv_info.define_path("AUTOMAKE_PERLLIBDIR", automake_dataroot_path)

        aclocal_bin = path.join(bin_path, "aclocal")
        self.output.info(f"Defining ACLOCAL environment variable: {aclocal_bin}")
        self.env_info.ACLOCAL = aclocal_bin
        self.buildenv_info.define_path("ACLOCAL", aclocal_bin)

        automake_bin = path.join(bin_path, "automake")
        self.output.info(f"Defining AUTOMAKE environment variable: {automake_bin}")
        self.env_info.AUTOMAKE = automake_bin
        self.buildenv_info.define_path("AUTOMAKE", automake_bin)

        compile_bin = path.join(automake_dataroot_path, "compile")
        self.output.info(f"Define path to `compile` binary in user_info as: {compile_bin}")
        self.user_info.compile = compile_bin  # FIXME: Conan V2 will use conf_key instead of user_info
        compile_conf_key = "user.automake:compile"
        self.output.info(f"Defining path to `compile` binary in configuration as `{compile_conf_key}` with value: {compile_bin}")
        self.conf_info.define(compile_conf_key, compile_bin)

        ar_lib_bin = path.join(automake_dataroot_path, "ar-lib")
        self.output.info(f"Define path to ar_lib binary in user_info as: {ar_lib_bin}")
        self.user_info.ar_lib = ar_lib_bin  # FIXME: Conan V2 will use conf_key instead of user_info
        ar_lib_conf_key = "user.automake:ar-lib"
        self.output.info(f"Defining path to ar-lib binary in configuration as `{ar_lib_conf_key}` with value: {ar_lib_bin}")
        self.conf_info.define(ar_lib_conf_key, ar_lib_bin)

        install_sh_bin = path.join(automake_dataroot_path, "install-sh")
        self.output.info(f"Define path to install_sh binary in user_info as: {install_sh_bin}")
        self.user_info.install_sh = install_sh_bin  # FIXME: Conan  V2 will use conf_key instead of user_info
        install_sh_conf_key = "user.automake:install-sh"
        self.output.info(f"Defining path to install_sh binary in configuration as `{install_sh_conf_key}` with value: {install_sh_bin}")
        self.conf_info.define(install_sh_conf_key, install_sh_bin)
