from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path, unix_path_package_info_legacy
from conan.tools.scm import Version

import os

required_conan_version = ">=1.57.0"


class GetTextConan(ConanFile):
    name = "gettext"
    package_type = "application"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

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

    def requirements(self):
        self.requires("libiconv/1.17")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.win_bash = True
            self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.build_requires("automake/1.16.5")

    def validate(self):
        if Version(self.version) < "0.21" and is_msvc(self):
            raise ConanInvalidConfiguration("MSVC builds of gettext for versions < 0.21 are not supported.")  # FIXME: it used to be possible. What changed?

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

        tc = AutotoolsToolchain(self)
        libiconv_prefix = unix_path(self, self.dependencies["libiconv"].package_folder)
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
       

        if is_msvc(self):
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS") #TODO: reference github issue

            env = Environment()
            compile_wrapper = self.dependencies.build["automake"].conf_info.get("user.automake:compile-wrapper")
            lib_wrapper = self.dependencies.build["automake"].conf_info.get("user.automake:lib-wrapper")
            env.define("CC", "{} cl -nologo".format(unix_path(self, compile_wrapper)))
            env.define("LD", "link -nologo")
            env.define("NM", "dumpbin -symbols")
            env.define("STRIP", ":")
            env.define("AR", "{} lib".format(unix_path(lib_wrapper)))
            env.define("RANLIB", ":")
            windres_arch = {"x86": "i686", "x86_64": "x86-64"}[str(self.settings.arch)]
            env.define("RC", f"windres --target=pe-{windres_arch}")
            env.vars(self).save_script("conanbuild_msvc")


        tc.generate()


    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "gettext-tools", "misc", "autopoint.in"), "@prefix@", "$GETTEXT_ROOT_UNIX")
        replace_in_file(self, os.path.join(self.source_folder, "gettext-tools", "misc", "autopoint.in"), "@datarootdir@", "$prefix/res")

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()


    def package(self):
        autotools = Autotools(self)
        autotools.install()
        
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
 
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "share", "info"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        aclocal = os.path.join(self.package_folder, "res", "aclocal")
        autopoint = os.path.join(self.package_folder, "bin", "autopoint")
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal)
        self.buildenv_info.define("AUTOPOINT", autopoint)
        self.buildenv_info.define("GETTEXT_ROOT_UNIX", self.package_folder)
        
        # TODO: the following can be removed when the recipe supports Conan >= 2.0 only
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(unix_path_package_info_legacy(self, aclocal))

        self.output.info("Setting AUTOPOINT environment variable: {}".format(autopoint))
        self.env_info.AUTOPOINT = unix_path_package_info_legacy(self, autopoint)
        self.env_info.GETTEXT_ROOT_UNIX = unix_path_package_info_legacy(self, self.package_folder)
