import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, chdir, rm, rename
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path, unix_path_package_info_legacy
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version

required_conan_version = ">=1.57.0"

class GetTextConan(ConanFile):
    name = "gettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = ("GPL-3.0-or-later", "LGPL-2.1-or-later")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": ["posix", "solaris", "pth", "windows", "disabled"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # INFO: Handle default value for `threads` in `config_options` method
    }

    @property
    def _gettext_folder(self):
        return "gettext-tools"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        self.options.threads = {"Solaris": "solaris", "Windows": "windows"}.get(str(self.settings.os), "posix")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
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
            "--disable-nls",
            "--disable-dependency-tracking",
            "--enable-relocatable",
            "--disable-c++",
            "--disable-java",
            "--disable-csharp",
            "--disable-libasprintf",
            "--disable-openmp",
            "--disable-curses",
            "--disable-threads" if self.options.threads == "disabled" else ("--enable-threads=" + str(self.options.threads)),
            "--with-included-glib",
            "--with-included-libxml",
            "--with-included-libunistring",
            "--with-installed-libtextstyle=no",
            "--without-cvs",
            "--without-emacs",
            "--without-git",
            "--without-libcurses-prefix",
            "--without-libncurses-prefix",
            "--without-libtermcap-prefix",
            "--without-libxcurses-prefix",
            "--without-included-gettext",
        ])

        if is_msvc(self):
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS") #TODO: reference github issue

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
        #with chdir(self, os.path.join(self.build_folder, self._gettext_folder)):
        #    autotools.make(args=["-C", "intl"])

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "share", "info"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        dest_lib_dir = os.path.join(self.package_folder, "lib")
        dest_runtime_dir = os.path.join(self.package_folder, "bin")
        dest_include_dir = os.path.join(self.package_folder, "include")
        copy(self, "*gnuintl*.dll", self.build_folder, dest_runtime_dir, keep_path=False)
        copy(self, "*gnuintl*.lib", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.a", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.so*", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.dylib", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*libgnuintl.h", self.build_folder, dest_include_dir, keep_path=False)
        rename(self, os.path.join(dest_include_dir, "libgnuintl.h"), os.path.join(dest_include_dir, "libintl.h"))

    def package_info(self):
        aclocal = os.path.join(self.package_folder, "res", "aclocal")
        autopoint = os.path.join(self.package_folder, "bin", "autopoint")
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal)
        self.buildenv_info.define_path("AUTOPOINT", autopoint)

        # TODO: Generate FindGettext.cmake: https://cmake.org/cmake/help/latest/module/FindGettext.html

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Intl")
        self.cpp_info.set_property("cmake_target_name", "Intl::Intl")
        self.cpp_info.libs = ["gnuintl"]
        if is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")

        # TODO: the following can be removed when the recipe supports Conan >= 2.0 only
        self.cpp_info.names["cmake_find_package"] = "Intl"
        self.cpp_info.names["cmake_find_package_multi"] = "Intl"
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(unix_path_package_info_legacy(self, aclocal))
        self.env_info.AUTOPOINT = unix_path_package_info_legacy(self, autopoint)
