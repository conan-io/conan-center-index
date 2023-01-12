import os

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.env import Environment
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
from conans import tools as tools_legacy


required_conan_version = ">=1.53.0"


class GetTextConan(ConanFile):
    name = "gettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler"
    generators = "VirtualBuildEnv", "AutotoolsDeps"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.build_requires("automake/1.16.5")

    def validate(self):
        if Version(self.version) < "0.21" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("MSVC builds of gettext for versions < 0.21 are not supported.")  # FIXME: it used to be possible. What changed?

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)

        libiconv_prefix = self.dependencies["libiconv"].package_folder

        tc.configure_args.extend([
            "HELP2MAN=/bin/true",
            "EMACS=no",
            "--datarootdir=${prefix}/res",
            "--with-libiconv-prefix={}".format(libiconv_prefix),
            "--disable-shared",
            "--disable-static",
            "--disable-nls",
            "--disable-dependency-tracking",
            "--enable-relocatable",
            "--disable-c++",
            "--disable-java",
            "--disable-csharp",
            "--disable-libasprintf",
            "--disable-curses",
        ])

        host = None
        if is_msvc(self):
            rc = None
            self._autotools.flags.append("-FS")
            # INSTALL.windows: Native binaries, built using the MS Visual C/C++ tool chain.
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
                rc = "windres --target=pe-i386"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
                rc = "windres --target=pe-x86-64"
            if rc:
                tc.configure_args.extend([
                    "RC={}".format(rc),
                    "WINDRES={}".format(rc),
                ])
            if host:
                tc.configure_args.append("--host={}".format(host))
        tc.generate()

        if is_msvc(self):
            env = Environment()
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")


    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "gettext-tools", "misc", "autopoint.in"), "@prefix@", "$GETTEXT_ROOT_UNIX")
        replace_in_file(self, os.path.join(self.source_folder, "gettext-tools", "misc", "autopoint.in"), "@datarootdir@", "$prefix/res")

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()



    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "share", "info"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))


    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.buildenv_info.append_path("PATH", bindir)

        aclocal = tools_legacy.unix_path(os.path.join(self.package_folder, "res", "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.buildenv_info.append_path("AUTOMAKE_CONAN_INCLUDES", aclocal)

        autopoint = tools_legacy.unix_path(os.path.join(self.package_folder, "bin", "autopoint"))
        self.output.info("Setting AUTOPOINT environment variable: {}".format(autopoint))
        self.buildenv_info.define_path("AUTOPOINT", autopoint)

        self.buildenv_info.GETTEXT_ROOT_UNIX = tools_legacy.unix_path(self.package_folder)

        # TODO: to remove in conan v2
        self.env_info.PATH.append(bindir)
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal)
        self.env_info.AUTOPOINT = autopoint
        self.env_info.GETTEXT_ROOT_UNIX = tools_legacy.unix_path(self.package_folder)
