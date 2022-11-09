from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, replace_in_file, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path, is_msvc
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.52.0"


class AutoconfConan(ConanFile):
    name = "autoconf"
    description = (
        "Autoconf is an extensible package of M4 macros that produce shell "
        "scripts to automatically configure software source code packages"
    )
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf/"
    topics = ("autoconf", "configure", "build")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("m4/1.4.19")

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
        ])

        if self.settings.os == "Windows":
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

        env = tc.environment()
        env.define_path("INSTALL", unix_path(self, os.path.join(self.source_folder, "build-aux", "install-sh")))
        tc.generate(env)

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"),
                        "M4 = /usr/bin/env m4", "#M4 = /usr/bin/env m4")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        # TODO: can be replaced by autotools.install() if required_conan_version = ">=1.54.0"
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "res", "info"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.resdirs = ["res"]

        # TODO: use legacy unix_path for the moment (see https://github.com/conan-io/conan/issues/12499)

        dataroot_path = tools_legacy.unix_path(os.path.join(self.package_folder, "res", "autoconf"))
        self.output.info(f"Defining AC_MACRODIR environment variable: {dataroot_path}")
        self.buildenv_info.define_path("AC_MACRODIR", dataroot_path)

        self.output.info(f"Defining AUTOM4TE_PERLLIBDIR environment variable: {dataroot_path}")
        self.buildenv_info.define_path("AUTOM4TE_PERLLIBDIR", dataroot_path)

        bin_path = os.path.join(self.package_folder, "bin")

        autoconf_bin = tools_legacy.unix_path(os.path.join(bin_path, "autoconf"))
        self.output.info(f"Defining AUTOCONF environment variable: {autoconf_bin}")
        self.buildenv_info.define_path("AUTOCONF", autoconf_bin)

        autoreconf_bin = tools_legacy.unix_path(os.path.join(bin_path, "autoreconf"))
        self.output.info(f"Defining AUTORECONF environment variable: {autoreconf_bin}")
        self.buildenv_info.define_path("AUTORECONF", autoreconf_bin)

        autoheader_bin = tools_legacy.unix_path(os.path.join(bin_path, "autoheader"))
        self.output.info(f"Defining AUTOHEADER environment variable: {autoheader_bin}")
        self.buildenv_info.define_path("AUTOHEADER", autoheader_bin)

        autom4te_bin = tools_legacy.unix_path(os.path.join(bin_path, "autom4te"))
        self.output.info(f"Defining AUTOM4TE environment variable: {autom4te_bin}")
        self.buildenv_info.define_path("AUTOM4TE", autom4te_bin)

        # TODO: to remove in conan v2
        self.env_info.PATH.append(bin_path)
        self.env_info.AC_MACRODIR = dataroot_path
        self.env_info.AUTOM4TE_PERLLIBDIR = dataroot_path
        self.env_info.AUTOCONF = autoconf_bin
        self.env_info.AUTORECONF = autoreconf_bin
        self.env_info.AUTOHEADER = autoheader_bin
        self.env_info.AUTOM4TE = autom4te_bin
