import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path, unix_path_package_info_legacy
from conan.tools.scm import Version

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

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if Version(self.version) < "0.21" and is_msvc(self):
            raise ConanInvalidConfiguration("MSVC builds of gettext for versions < 0.21 are not supported.")  # FIXME: it used to be possible. What changed?

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        
        if self.version >= Version("0.22") or is_msvc(self):
            self.build_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        libiconv = self.dependencies["libiconv"]
        libiconv_root = unix_path(self, libiconv.package_folder)
        tc.configure_args.extend([
            "HELP2MAN=/bin/true",
            "EMACS=no",
            "--datarootdir=${prefix}/res",
            "--with-libiconv-prefix={}".format(libiconv_root),
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

            # prevent redefining compiler instrinsic functions
            tc.configure_args.extend([
                'ac_cv_func_memmove=yes',
                'ac_cv_func_memset=yes'
            ])

            # The flag above `--with-libiconv-prefix` fails to correctly detect libiconv on windows+msvc
            # so it needs an extra nudge. We could use `AutotoolsDeps` but it's currently affected by the
            # following outstanding issue: https://github.com/conan-io/conan/issues/12784
            iconv_includedir = unix_path(self, libiconv.cpp_info.aggregated_components().includedirs[0])
            iconv_libdir = unix_path(self, libiconv.cpp_info.aggregated_components().libdirs[0])
            tc.extra_cflags.append(f"-I{iconv_includedir}")
            tc.extra_ldflags.append(f"-L{iconv_libdir}")

            env = Environment()
            compile_wrapper = self.dependencies.build["automake"].conf_info.get("user.automake:compile-wrapper")
            lib_wrapper = self.dependencies.build["automake"].conf_info.get("user.automake:lib-wrapper")
            env.define("CC", "{} cl -nologo".format(unix_path(self, compile_wrapper)))
            env.define("LD", "link -nologo")
            env.define("NM", "dumpbin -symbols")
            env.define("STRIP", ":")
            env.define("AR", "{} lib".format(unix_path(self, lib_wrapper)))
            env.define("RANLIB", ":")

            # One of the checks performed by the configure script requires this as a preprocessor flag
            # rather than a C compiler flag
            env.prepend("CPPFLAGS", f"-I{iconv_includedir}")

            windres_arch = {"x86": "i686", "x86_64": "x86-64"}[str(self.settings.arch)]
            env.define("RC", f"windres --target=pe-{windres_arch}")
            env.vars(self).save_script("conanbuild_msvc")

        tc.generate()

    def build(self):
        apply_conandata_patches(self)

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
        self.buildenv_info.define_path("AUTOPOINT", autopoint)

        # TODO: the following can be removed when the recipe supports Conan >= 2.0 only
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(unix_path_package_info_legacy(self, aclocal))
        self.env_info.AUTOPOINT = unix_path_package_info_legacy(self, autopoint)
