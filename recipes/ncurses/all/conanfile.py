from conan import ConanFile
from conans.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches, save, copy
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, check_min_vs, unix_path
from conan.tools.build import cross_building
from conan.tools.scm import Version
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.env import Environment, VirtualRunEnv, VirtualBuildEnv
import os
import textwrap

required_conan_version = ">=1.54.0"


class NCursesConan(ConanFile):
    name = "ncurses"
    description = "The ncurses (new curses) library is a free software emulation of curses in System V Release 4.0 (SVr4), and more"
    topics = ("ncurses", "terminal", "screen", "tui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/ncurses"
    license = "X11"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_widec": [True, False],
        "with_extended_colors": [True, False],
        "with_cxx": [True, False],
        "with_progs": [True, False],
        "with_ticlib": ["auto", True, False],
        "with_reentrant": [True, False],
        "with_tinfo": ["auto", True, False],
        "with_pcre2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_widec": True,
        "with_extended_colors": True,
        "with_cxx": True,
        "with_progs": True,
        "with_ticlib": "auto",
        "with_reentrant": False,
        "with_tinfo": "auto",
        "with_pcre2": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _with_ticlib(self):
        if self.options.with_ticlib == "auto":
            return self.settings.os != "Windows"
        else:
            return self.options.with_ticlib

    @property
    def _with_tinfo(self):
        if self.options.with_tinfo == "auto":
            return self.settings.os != "Windows"
        else:
            return self.options.with_tinfo

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options.with_ticlib = self._with_ticlib
        self.options.with_tinfo  = self._with_tinfo

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if not self.options.with_widec:
            del self.options.with_extended_colors

    def requirements(self):
        if self.options.with_pcre2:
            self.requires("pcre2/10.37")
        if is_msvc(self):
            self.requires("getopt-for-visual-studio/20200201")
            self.requires("dirent/1.23.2")
            if self.options.get_safe("with_extended_colors", False):
                self.requires("naive-tsearch/0.1.1")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def validate(self):
        if any("arm" in arch for arch in (self.settings.arch, self._settings_build.arch)) and cross_building(self):
            # FIXME: Cannot build ncurses from x86_64 to armv8 (Apple M1).  Cross building from Linux/x86_64 to Mingw/x86_64 works flawless.
            # FIXME: Need access to environment of build profile to set build compiler (BUILD_CC/CC_FOR_BUILD)
            raise ConanInvalidConfiguration("Cross building to/from arm is (currently) not supported")
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Cannot build shared libraries with static (MT) runtime")
        if self.settings.os == "Windows":
            if self._with_tinfo:
                raise ConanInvalidConfiguration("terminfo cannot be built on Windows because it requires a term driver")
            if self.options.shared and self._with_ticlib:
                raise ConanInvalidConfiguration("ticlib cannot be built separately as a shared library on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        # inject tool_requires env vars in build scope (not needed if there is no tool_requires)
        env = VirtualBuildEnv(self)
        env.generate()
        # inject requires env vars in build scope
        # it's required in case of native build when there is AutotoolsDeps & at least one dependency which might be shared, because configure tries to run a test executable
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--with-shared={}".format(yes_no(self.options.shared)),
            "--with-cxx-shared={}".format(yes_no(self.options.shared)),
            "--with-normal={}".format(yes_no(not self.options.shared)),
            "--enable-widec={}".format(yes_no(self.options.with_widec)),
            "--enable-ext-colors={}".format(yes_no(self.options.get_safe("with_extended_colors", False))),
            "--enable-reentrant={}".format(yes_no(self.options.with_reentrant)),
            "--with-pcre2={}".format(yes_no(self.options.with_pcre2)),
            "--with-cxx-binding={}".format(yes_no(self.options.with_cxx)),
            "--with-progs={}".format(yes_no(self.options.with_progs)),
            "--with-termlib={}".format(yes_no(self._with_tinfo)),
            "--with-ticlib={}".format(yes_no(self._with_ticlib)),
            "--without-libtool",
            "--without-ada",
            "--without-manpages",
            "--without-tests",
            "--disable-echo",
            "--without-debug",
            "--without-profile",
            "--with-sp-funcs",
            "--disable-rpath",
            "--datarootdir={}".format(unix_path(self, os.path.join(self.package_folder, "res"))),
            "--disable-pc-files",
        ])
        if self.settings.os == "Windows":
            tc.configure_args.extend([
                "--disable-macros",
                "--disable-termcap",
                "--enable-database",
                "--enable-sp-funcs",
                "--enable-term-driver",
                "--enable-interop",
            ])
        if is_msvc(self):
            tc.configure_args.extend([
                "ac_cv_func_getopt=yes",
                "ac_cv_func_setvbuf_reversed=no",
            ])
            tc.extra_cxxflags.append("-EHsc")
            if check_min_vs(self, 180, raise_invalid=False):
                tc.extra_cflags.append("-FS")
        if (self.settings.os, self.settings.compiler) == ("Windows", "gcc"):
            # add libssp (gcc support library) for some missing symbols (e.g. __strcpy_chk)
            tc.extra_ldflags.extend(["-lmingwex", "-lssp"])
        tc.generate()

        # generate pkg-config files of dependencies (useless if upstream configure.ac doesn't rely on PKG_CHECK_MODULES macro)
        tc = PkgConfigDeps(self)
        tc.generate()
        # generate dependencies for autotools
        tc = AutotoolsDeps(self)
        tc.generate()

        # If Visual Studio is supported
        if is_msvc(self):
            env = Environment()
            # get compile & ar-lib from automake (or eventually lib source code if available)
            # it's not always required to wrap CC, CXX & AR with these scripts, it depends on how much love was put in
            # upstream build files
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
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
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    @property
    def _major_version(self):
        return Version(self.version).major

    @staticmethod
    def _create_cmake_module_alias_targets(module_file):
        save(ConanFile, module_file, textwrap.dedent("""\
            set(CURSES_FOUND ON)
            get_target_property(CURSES_INCLUDE_DIRS  ncurses::libcurses INTERFACE_INCLUDE_DIRECTORIES)
            get_target_property(CURSES_LIBRARIES     ncurses::libcurses INTERFACE_LINK_LIBRARIES)
            get_target_property(_curses_compile_opts ncurses::libcurses INTERFACE_COMPILE_OPTIONS)
            get_target_property(_curses_compile_defs ncurses::libcurses INTERFACE_COMPILE_DEFINITIONS)
            set(CURSES_CFLAGS ${_curses_compile_opts} ${_curses_compile_defs})
            set(CURSES_HAVE_CURSES_H ON)
            set(CURSES_HAVE_NCURSES_H ON)
            if(CURSES_NEED_NCURSES)
                set(CURSES_HAVE_NCURSES_CURSES_H ON)
                set(CURSES_HAVE_NCURSES_NCURSES_H ON)
            endif()

            # Backward Compatibility
            set(CURSES_INCLUDE_DIR ${CURSES_INCLUDE_DIRS})
            set(CURSES_LIBRARY ${CURSES_LIBRARIES})
        """))

    def package(self):
        # return
        copy(self, "COPYING", src=self.source_folder, dst="licenses")
        autotools = Autotools(self)
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "bin", "ncurses{}{}-config".format(self._suffix, self._major_version)))

        self._create_cmake_module_alias_targets(os.path.join(self.package_folder, self._module_subfolder, self._module_file))

    @property
    def _suffix(self):
        res = ""
        if self.options.with_reentrant:
            res += "t"
        if self.options.with_widec:
            res += "w"
        return res

    @property
    def _lib_suffix(self):
        res = self._suffix
        if self.options.shared:
            if self.settings.os == "Windows":
                res += ".dll"
        return res

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "CursesFindModuleBackwardCompat.cmake".format(self.name)

    def package_info(self):
        module_rel_path = os.path.join(self._module_subfolder, self._module_file)
        self.cpp_info.set_property("cmake_file_name", "Curses")
        self.cpp_info.set_property("cmake_build_modules", [module_rel_path])

        if self._with_tinfo:
            self.cpp_info.components["tinfo"].libs = ["tinfo" + self._lib_suffix]
            self.cpp_info.components["tinfo"].names["pkg_config"] = "tinfo" + self._lib_suffix
            self.cpp_info.components["tinfo"].includedirs.append(os.path.join("include", "ncurses" + self._suffix))

        self.cpp_info.components["libcurses"].libs = ["ncurses" + self._lib_suffix]
        self.cpp_info.components["libcurses"].names["pkg_config"] = "ncurses" + self._lib_suffix
        self.cpp_info.components["libcurses"].includedirs.append(os.path.join("include", "ncurses" + self._suffix))
        if not self.options.shared:
            self.cpp_info.components["libcurses"].defines = ["NCURSES_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libcurses"].system_libs = ["dl", "m"]
        if self._with_tinfo:
            self.cpp_info.components["libcurses"].requires.append("tinfo")

        if is_msvc(self):
            self.cpp_info.components["libcurses"].requires.extend([
                "getopt-for-visual-studio::getopt-for-visual-studio",
                "dirent::dirent",
            ])
            if self.options.get_safe("with_extended_colors", False):
                self.cpp_info.components["libcurses"].requires.append("naive-tsearch::naive-tsearch")

        self.cpp_info.components["panel"].libs = ["panel" + self._lib_suffix]
        self.cpp_info.components["panel"].names["pkg_config"] = "panel" + self._lib_suffix
        self.cpp_info.components["panel"].requires = ["libcurses"]

        self.cpp_info.components["menu"].libs = ["menu" + self._lib_suffix]
        self.cpp_info.components["menu"].names["pkg_config"] = "menu" + self._lib_suffix
        self.cpp_info.components["menu"].requires = ["libcurses"]

        self.cpp_info.components["form"].libs = ["form" + self._lib_suffix]
        self.cpp_info.components["form"].names["pkg_config"] = "form" + self._lib_suffix
        self.cpp_info.components["form"].requires = ["libcurses"]
        if self.options.with_pcre2:
            self.cpp_info.components["form"].requires.append("pcre2::pcre2")

        if self.options.with_cxx:
            self.cpp_info.components["curses++"].libs = ["ncurses++" + self._lib_suffix]
            self.cpp_info.components["curses++"].names["pkg_config"] = "ncurses++" + self._lib_suffix
            self.cpp_info.components["curses++"].requires = ["libcurses"]

        if self._with_ticlib:
            self.cpp_info.components["ticlib"].libs = ["tic" + self._lib_suffix]
            self.cpp_info.components["ticlib"].names["pkg_config"] = "tic" + self._lib_suffix
            self.cpp_info.components["ticlib"].requires = ["libcurses"]

        if self.options.with_progs:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        terminfo = os.path.join(self.package_folder, "res", "terminfo")
        self.output.info("Setting TERMINFO environment variable: {}".format(terminfo))
        self.buildenv_info.define_path("TERMINFO", terminfo)
        self.runenv_info.define_path("TERMINFO", terminfo)
        self.env_info.TERMINFO = terminfo

        self.user_info.lib_suffix = self._lib_suffix
