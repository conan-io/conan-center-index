from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class NCursesConan(ConanFile):
    name = "ncurses"
    description = "The ncurses (new curses) library is a free software emulation of curses in System V Release 4.0 (SVr4), and more"
    topics = ("curses", "terminal", "screen", "tui")
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def _with_ticlib(self, options=None, settings=None):
        if options is None:
            options = self.options
        if settings is None:
            settings = self.settings
        if options.with_ticlib == "auto":
            return settings.os != "Windows"
        return options.with_ticlib

    def _with_tinfo(self, options=None, settings=None):
        if options is None:
            options = self.options
        if settings is None:
            settings = self.settings
        if options.with_tinfo == "auto":
            return settings.os != "Windows"
        return options.with_tinfo

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")
        if not self.options.with_widec:
            self.options.rm_safe("with_extended_colors")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_pcre2:
            self.requires("pcre2/10.42")
        if is_msvc(self):
            self.requires("getopt-for-visual-studio/20200201")
            self.requires("dirent/1.23.2")
            if self.options.get_safe("with_extended_colors", False):
                self.requires("naive-tsearch/0.1.1")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def validate(self):
        if any("arm" in arch for arch in (self.settings.arch, self._settings_build.arch)) and cross_building(self):
            # FIXME: Cannot build ncurses from x86_64 to armv8 (Apple M1).  Cross building from Linux/x86_64 to Mingw/x86_64 works flawless.
            # FIXME: Need access to environment of build profile to set build compiler (BUILD_CC/CC_FOR_BUILD)
            raise ConanInvalidConfiguration("Cross building to/from arm is (currently) not supported")
        if self.options.shared and is_msvc(self) and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Cannot build shared libraries with static (MT) runtime")
        if self.settings.os == "Windows":
            if self._with_tinfo():
                raise ConanInvalidConfiguration("terminfo cannot be built on Windows because it requires a term driver")
            if self.options.shared and self._with_ticlib():
                raise ConanInvalidConfiguration("ticlib cannot be built separately as a shared library on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        def yes_no(v):
            if v:
                return "yes"
            return "no"
        tc.configure_args.extend([
            f"--with-shared={yes_no(self.options.shared)}",
            f"--with-cxx-shared={yes_no(self.options.shared)}",
            f"--with-normal={yes_no(not self.options.shared)}",
            f"--enable-widec={yes_no(self.options.with_widec)}",
            f"--enable-ext-colors={yes_no(self.options.get_safe('with_extended_colors', False))}",
            f"--enable-reentrant={yes_no(self.options.with_reentrant)}",
            f"--with-pcre2={yes_no(self.options.with_pcre2)}",
            f"--with-cxx-binding={yes_no(self.options.with_cxx)}",
            f"--with-progs={yes_no(self.options.with_progs)}",
            f"--with-termlib={yes_no(self._with_tinfo())}",
            f"--with-ticlib={yes_no(self._with_ticlib())}",
            "--without-libtool",
            "--without-ada",
            "--without-manpages",
            "--without-tests",
            "--disable-echo",
            "--without-debug",
            "--without-profile",
            "--with-sp-funcs",
            "--disable-rpath",
            "--disable-pc-files",
        ])
        build = None
        host = None
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
            build = host = f"{self.settings.arch}-w64-mingw32-msvc"
            tc.configure_args.extend([
                "ac_cv_func_getopt=yes",
                "ac_cv_func_setvbuf_reversed=no",
            ])
            tc.extra_cxxflags.append("-EHsc")
            if Version(self.settings.compiler.version) >= 12:
                tc.extra_cflags.append("-FS")
        if (self.settings.os, self.settings.compiler) == ("Windows", "gcc"):
            # add libssp (gcc support library) for some missing symbols (e.g. __strcpy_chk)
            tc.extra_ldflags.extend(["-lmingwex", "-lssp"])
        if build:
            tc.configure_args.append(f"ac_cv_build={build}")
        if host:
            tc.configure_args.append(f"ac_cv_host={host}")
            tc.configure_args.append(f"ac_cv_target={host}")
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

        if is_msvc(self):
            env = Environment()
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", "lib -nologo")
            env.define("NM", "dumpbin -symbols")
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

    def _create_cmake_module_alias_targets(self, module_file):
        save(self, module_file, textwrap.dedent("""\
            set(CURSES_FOUND ON)
            set(CURSES_INCLUDE_DIRS $<TARGET_PROPERTY:ncurses::libcurses,INTERFACE_INCLUDE_DIRECTORIES>)
            set(CURSES_LIBRARIES ncurses::libcurses)
            set(CURSES_CFLAGS $<TARGET_PROPERTY:ncurses::libcurses,INTERFACE_COMPILE_DEFINITIONS>)
            set(CURSES_HAVE_CURSES_H OFF)
            set(CURSES_HAVE_NCURSES_H OFF)
            if(CURSES_NEED_NCURSES)
                set(CURSES_HAVE_NCURSES_CURSES_H ON)
                set(CURSES_HAVE_NCURSES_NCURSES_H ON)
            endif()

            # Backward Compatibility
            set(CURSES_INCLUDE_DIR ${CURSES_INCLUDE_DIRS})
            set(CURSES_LIBRARY ${CURSES_LIBRARIES})
        """))

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))
        rm(self, "terminfo", os.path.join(self.package_folder, "lib"))
        rm(self, f"ncurses{self._suffix}{self._major_version}-config", os.path.join(self.package_folder, "bin"))

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

    def package_id(self):
        self.info.options.with_ticlib = self._with_ticlib(self.info.options, self.info.settings)
        self.info.options.with_tinfo = self._with_tinfo(self.info.options, self.info.settings)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return f"conan-official-{self.name}-targets.cmake"

    def _package_info_for_components(self):
        if self._with_tinfo():
            self.cpp_info.components["tinfo"].libs = [f"tinfo{self._lib_suffix}"]
            self.cpp_info.components["tinfo"].set_property("pkg_config_name", f"tinfo{self._lib_suffix}")
            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components["tinfo"].names["pkg_config"] = f"tinfo{self._lib_suffix}"
            self.cpp_info.components["tinfo"].includedirs.append(os.path.join("include", f"ncurses{self._suffix}"))

        self.cpp_info.components["libcurses"].libs = [f"ncurses{self._lib_suffix}"]
        self.cpp_info.components["libcurses"].set_property("pkg_config_name", f"ncurses{self._lib_suffix}")
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libcurses"].names["pkg_config"] = f"ncurses{self._lib_suffix}"
        self.cpp_info.components["libcurses"].includedirs.append(os.path.join("include", f"ncurses{self._suffix}"))
        if not self.options.shared:
            self.cpp_info.components["libcurses"].defines = ["NCURSES_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libcurses"].system_libs = ["dl", "m"]
        if self._with_tinfo():
            self.cpp_info.components["libcurses"].requires.append("tinfo")

        if is_msvc(self):
            self.cpp_info.components["libcurses"].requires.extend([
                "getopt-for-visual-studio::getopt-for-visual-studio",
                "dirent::dirent",
            ])
            if self.options.get_safe("with_extended_colors", False):
                self.cpp_info.components["libcurses"].requires.append("naive-tsearch::naive-tsearch")

        module_rel_path = os.path.join(self._module_subfolder, self._module_file)
        self.cpp_info.set_property("cmake_build_modules", [module_rel_path])
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libcurses"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["libcurses"].build_modules["cmake_find_package"] = [module_rel_path]
        self.cpp_info.components["libcurses"].build_modules["cmake_find_package_multi"] = [module_rel_path]

        self.cpp_info.components["panel"].libs = [f"panel{self._lib_suffix}"]
        self.cpp_info.components["panel"].set_property("pkg_config_name", f"panel{self._lib_suffix}")
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["panel"].names["pkg_config"] = f"panel{self._lib_suffix}"
        self.cpp_info.components["panel"].requires = ["libcurses"]

        self.cpp_info.components["menu"].libs = [f"menu{self._lib_suffix}"]
        self.cpp_info.components["menu"].set_property("pkg_config_name", f"menu{self._lib_suffix}")
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["menu"].names["pkg_config"] = f"menu{self._lib_suffix}"
        self.cpp_info.components["menu"].requires = ["libcurses"]

        self.cpp_info.components["form"].libs = [f"form{self._lib_suffix}"]
        self.cpp_info.components["form"].set_property("pkg_config_name", f"form{self._lib_suffix}")
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["form"].names["pkg_config"] = f"form{self._lib_suffix}"
        self.cpp_info.components["form"].requires = ["libcurses"]
        if self.options.with_pcre2:
            self.cpp_info.components["form"].requires.append("pcre2::pcre2")

        if self.options.with_cxx:
            self.cpp_info.components["curses++"].libs = [f"ncurses++{self._lib_suffix}"]
            self.cpp_info.components["curses++"].set_property("pkg_config_name", f"ncurses++{self._lib_suffix}")
            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components["curses++"].names["pkg_config"] = f"ncurses++{self._lib_suffix}"
            self.cpp_info.components["curses++"].requires = ["libcurses"]

        if self._with_ticlib():
            self.cpp_info.components["ticlib"].libs = [f"tic{self._lib_suffix}"]
            self.cpp_info.components["ticlib"].set_property("pkg_config_name", f"tic{self._lib_suffix}")
            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components["ticlib"].names["pkg_config"] = f"tic{self._lib_suffix}"
            self.cpp_info.components["ticlib"].requires = ["libcurses"]


    def package_info(self):
        self.cpp_info.set_property("cmake_module_file_name", "Curses")
        self.cpp_info.set_property("cmake_find_mode", "module")
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Curses"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Curses"

        self._package_info_for_components()

        if self.options.with_progs:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.runenv_info.append_path("PATH", bin_path)
            # TODO: For legacy 1.x downstream consumers, remove once recipe is 2.0 only:
            self.env_info.PATH.append(bin_path)

        terminfo = os.path.join(self.package_folder, "res", "terminfo")
        self.output.info(f"Setting TERMINFO environment variable: {terminfo}")
        self.runenv_info.define("TERMINFO", terminfo)
        # TODO: For legacy 1.x downstream consumers, remove once recipe is 2.0 only:
        self.env_info.TERMINFO = terminfo

        self.conf_info.define("user.ncurses:suffix", self._lib_suffix)
        # FIXME: to remove in conan v2
        self.user_info.lib_suffix = self._lib_suffix
