from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path, is_msvc

required_conan_version = ">=1.51.3"


class AutoconfConan(ConanFile):
    name = "autoconf"
    description = "Autoconf is an extensible package of M4 macros that produce shell scripts to automatically configure software source code packages"
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf/"
    topics = ("autoconf", "configure", "build")
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

    def layout(self):
        basic_layout(self, src_folder="autoconf")

    def requirements(self):
        self.requires("m4/1.4.19")

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")
        self.tool_requires("m4/1.4.19")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
        ])

        if self.settings.os == "Windows":
            if is_msvc(self):
                build = "{}-{}-{}".format(
                    "x86_64" if self._settings_build.arch == "x86_64" else "i686",
                    "pc" if self._settings_build.arch == "x86" else "win64",
                    "mingw64")
                host = "{}-{}-{}".format(
                    "x86_64" if self.settings.arch == "x86_64" else "i686",
                    "pc" if self.settings.arch == "x86" else "win64",
                    "mingw64")
                tc.configure_args.append(f"--build={build}")
                tc.configure_args.append(f"--host={host}")

        env = tc.environment()
        env.define("INSTALL", unix_path(self, str(self.source_path.joinpath('build-aux', 'install-sh'))))
        tc.generate(env)

        deps = AutotoolsDeps(self)
        deps.generate()

        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem

        copy(self, "COPYING*", src=self.source_folder, dst=self.package_path.joinpath("licenses"))
        rmdir(self, self.package_path.joinpath("res", "info"))
        rmdir(self, self.package_path.joinpath("res", "man"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = self.package_path.joinpath("bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(str(bin_path))

        dataroot_path = self.package_path.joinpath("res", "autoconf")
        self.output.info(f"Defining AC_MACRODIR environment variable: {dataroot_path}")
        self.env_info.AC_MACRODIR = str(dataroot_path)
        self.buildenv_info.define_path("AC_MACRODIR", str(dataroot_path))

        self.output.info(f"Defining AUTOM4TE_PERLLIBDIR environment variable: {dataroot_path}")
        self.env_info.AUTOM4TE_PERLLIBDIR = str(dataroot_path)
        self.buildenv_info.define_path("AUTOM4TE_PERLLIBDIR", str(dataroot_path))

        autoconf_bin = bin_path.joinpath("autoconf")
        self.output.info(f"Defining AUTOCONF environment variable: {autoconf_bin}")
        self.env_info.AUTOCONF = str(autoconf_bin)
        self.buildenv_info.define_path("AUTOCONF", str(autoconf_bin))

        autoconf_bin_conf_key = "tools.autoconf:autoconf"
        self.output.info(f"Defining path to autoconf binary in configuration as `{autoconf_bin_conf_key}` with value: {autoconf_bin}")
        self.conf_info.define(autoconf_bin_conf_key, str(autoconf_bin))

        autoreconf_bin = bin_path.joinpath("autoreconf")
        self.output.info(f"Defining AUTORECONF environment variable: {autoreconf_bin}")
        self.env_info.AUTORECONF = str(autoreconf_bin)
        self.buildenv_info.define_path("AUTORECONF", str(autoreconf_bin))

        autoreconf_bin_conf_key = "tools.autoconf:autoreconf"
        self.output.info(f"Defining path to autoreconf binary in configuration as `{autoreconf_bin_conf_key}` with value: {autoreconf_bin}")
        self.conf_info.define(autoreconf_bin_conf_key, str(autoreconf_bin))

        autoheader_bin = bin_path.joinpath("autoheader")
        self.output.info(f"Defining AUTOHEADER environment variable: {autoheader_bin}")
        self.env_info.AUTOHEADER = str(autoheader_bin)
        self.buildenv_info.define_path("AUTOHEADER", str(autoheader_bin))

        autoheader_bin_conf_key = "tools.autoconf:autoheader"
        self.output.info(f"Defining path to autoheader binary in configuration as `{autoheader_bin_conf_key}` with value: {autoheader_bin}")
        self.conf_info.define(autoheader_bin_conf_key, str(autoheader_bin))

        autom4te_bin = bin_path.joinpath("autom4te")
        self.output.info(f"Defining AUTOM4TE environment variable: {autom4te_bin}")
        self.env_info.AUTOM4TE = str(autom4te_bin)
        self.buildenv_info.define_path("AUTOM4TE", str(autom4te_bin))

        autom4te_bin_conf_key = "tools.autoconf:autom4te"
        self.output.info(f"Defining path to autom4te binary in configuration as `{autom4te_bin_conf_key}` with value: {autom4te_bin}")
        self.conf_info.define(autom4te_bin_conf_key, str(autom4te_bin))
