from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.51.3"


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

    @property
    def win_bash(self):
        return self._settings_build.os == "Windows"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def configure(self):
        try:
            del self.settings.compiler.libcxx  # for plain C projects only
        except ValueError:
            pass
        try:
            del self.settings.compiler.cppstd  # for plain C projects only
        except ValueError:
            pass

    def layout(self):
        basic_layout(self, src_folder="automake")

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
            replace_in_file(self, self.source_path.joinpath("bin", "aclocal.in"),
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

        copy(self, "COPYING*", src=self.source_folder, dst=self.package_path.joinpath("licenses"))
        rmdir(self, self.package_path.joinpath("res", "info"))
        rmdir(self, self.package_path.joinpath("res", "man"))
        rmdir(self, self.package_path.joinpath("res", "doc"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = self.package_path.joinpath("bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(str(bin_path))

        dataroot_path = self.package_path.joinpath("res")
        self.output.info(f"Defining AUTOMAKE_DATADIR environment variable: {dataroot_path}")
        self.env_info.AUTOMAKE_DATADIR = str(dataroot_path)
        self.buildenv_info.define_path("AUTOMAKE_DATADIR", str(dataroot_path))

        version = Version(self.version)
        automake_dataroot_path = dataroot_path.joinpath(f"automake-{version.major}.{version.minor}")
        self.output.info(f"Defining AUTOMAKE_LIBDIR environment variable: {automake_dataroot_path}")
        self.env_info.AUTOMAKE_LIBDIR = str(automake_dataroot_path)
        self.buildenv_info.define_path("AUTOMAKE_LIBDIR", str(automake_dataroot_path))

        self.output.info(f"Defining AUTOMAKE_PERLLIBDIR environment variable: {automake_dataroot_path}")
        self.env_info.AUTOMAKE_PERLLIBDIR = str(automake_dataroot_path)
        self.buildenv_info.define_path("AUTOMAKE_PERLLIBDIR", str(automake_dataroot_path))

        aclocal_bin = bin_path.joinpath("aclocal")
        self.output.info(f"Defining ACLOCAL environment variable: {aclocal_bin}")
        self.env_info.ACLOCAL = str(aclocal_bin)
        self.buildenv_info.define_path("ACLOCAL", str(aclocal_bin))

        aclocal_bin_conf_key = "tools.automake:aclocal"
        self.output.info(f"Defining path to aclocal binary in configuration as `{aclocal_bin_conf_key}` with value: {aclocal_bin}")
        self.conf_info.define(aclocal_bin_conf_key, str(aclocal_bin))

        automake_bin = bin_path.joinpath("automake")
        self.output.info(f"Defining AUTOMAKE environment variable: {automake_bin}")
        self.env_info.AUTOMAKE = str(automake_bin)
        self.buildenv_info.define_path("AUTOMAKE", str(automake_bin))

        automake_bin_conf_key = "tools.automake:automake"
        self.output.info(f"Defining path to automake binary in configuration as `{automake_bin_conf_key}` with value: {automake_bin}")
        self.conf_info.define(automake_bin_conf_key, str(automake_bin))

        compile_bin = automake_dataroot_path.joinpath("compile")
        self.output.info(f"Define path to `compile` binary in user_info as: {compile_bin}")
        self.user_info.compile = str(compile_bin)
        compile_conf_key = "tools.automake:compile"
        self.output.info(f"Defining path to `compile` binary in configuration as `{compile_conf_key}` with value: {compile_bin}")
        self.conf_info.define(compile_conf_key, str(compile_bin))

        ar_lib_bin = automake_dataroot_path.joinpath("ar-lib")
        self.output.info(f"Define path to ar_lib binary in user_info as: {ar_lib_bin}")
        self.user_info.ar_lib = str(ar_lib_bin)
        ar_lib_conf_key = "tools.automake:ar-lib"
        self.output.info(f"Defining path to ar-lib binary in configuration as `{ar_lib_conf_key}` with value: {ar_lib_bin}")
        self.conf_info.define(ar_lib_conf_key, str(ar_lib_bin))

        install_sh_bin = automake_dataroot_path.joinpath("install-sh")
        self.output.info(f"Define path to install_sh binary in user_info as: {install_sh_bin}")
        self.user_info.install_sh = str(install_sh_bin)
        install_sh_conf_key = "tools.automake:install-sh"
        self.output.info(f"Defining path to install_sh binary in configuration as `{install_sh_conf_key}` with value: {install_sh_bin}")
        self.conf_info.define(install_sh_conf_key, str(install_sh_bin))
