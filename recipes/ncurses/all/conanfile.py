from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import textwrap


class NCursesConan(ConanFile):
    name = "ncurses"
    description = "The ncurses (new curses) library is a free software emulation of curses in System V Release 4.0 (SVr4), and more"
    topics = ("conan", "ncurses", "terminal", "screen", "tui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/ncurses"
    license = "X11"
    exports_sources = "patches/**"
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
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

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            if self.settings.compiler == "Visual Studio":
                if "MT" in str(self.settings.compiler.runtime):
                    raise ConanInvalidConfiguration("Cannot build shared libraries with static (MT) runtime")
        if not self.options.with_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if not self.options.with_widec:
            del self.options.with_extended_colors
        if self.settings.os == "Windows":
            if self._with_tinfo:
                raise ConanInvalidConfiguration("terminfo cannot be built on Windows because it requires a term driver")
            if self.options.shared and self._with_ticlib:
                raise ConanInvalidConfiguration("ticlib cannot be built separately as a shared library on Windows")

    def requirements(self):
        if self.options.with_pcre2:
            self.requires("pcre2/10.33")
        if self.settings.compiler == "Visual Studio":
            self.requires("getopt-for-visual-studio/20200201")
            self.requires("dirent/1.23.2")
            if self.options.get_safe("with_extended_colors", False):
                self.requires("naive-tsearch/0.1.1")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ncurses-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        build = None
        host = None
        conf_args = [
            "--enable-widec" if self.options.with_widec else "--disable-widec",
            "--enable-ext-colors" if self.options.get_safe("with_extended_colors", False) else "--disable-ext-colors",
            "--enable-reentrant" if self.options.with_reentrant else "--disable-reentrant",
            "--with-pcre2" if self.options.with_pcre2 else "--without-pcre2",
            "--with-cxx-binding" if self.options.with_cxx else "--without-cxx-binding",
            "--with-progs" if self.options.with_progs else "--without-progs",
            "--with-termlib" if self._with_tinfo else "--without-termlib",
            "--with-ticlib" if self._with_ticlib else "--without-ticlib",
            "--without-libtool",
            "--without-ada",
            "--without-manpages",
            "--without-tests",
            "--disable-echo",
            "--without-debug",
            "--without-profile",
            "--with-sp-funcs",
            "--disable-rpath",
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin", "share"))),
            "--disable-pc-files",
        ]
        if self.options.shared:
            conf_args.extend(["--with-shared", "--without-normal", "--with-cxx-shared",])
        else:
            conf_args.extend(["--without-shared", "--with-normal", "--without-cxx-shared"])
        if self.settings.os == "Windows":
            conf_args.extend([
                "--disable-macros",
                "--disable-termcap",
                "--enable-database",
                "--enable-sp-funcs",
                "--enable-term-driver",
                "--enable-interop",
            ])
        if self.settings.compiler == "Visual Studio":
            conf_args.extend([
                "ac_cv_func_getopt=yes",
                "ac_cv_func_setvbuf_reversed=no",
            ])
            build = host = "{}-w64-mingw32-msvc7".format(self.settings.arch)
            self._autotools.flags.append("-FS")
            self._autotools.cxx_flags.append("-EHsc")
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder, host=host, build=build)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                msvc_env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                    "LDFLAGS": "",
                    "NM": "dumpbin -symbols",
                    "STRIP": ":",
                    "AR": "lib -nologo",
                    "RANLIB": ":",
                }
                with tools.environment_append(msvc_env):
                    yield
        else:
            yield

    def build(self):
        self._patch_sources()
        # return
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _major_version(self):
        return tools.Version(self.version).major


    @staticmethod
    def _create_cmake_module_alias_targets(module_file):
        tools.save(module_file, textwrap.dedent("""\
            set(CURSES_FOUND ON)
            set(CURSES_INCLUDE_DIRS ${ncurses_libcurses_INCLUDE_DIRS})
            set(CURSES_LIBRARIES ${ncurses_libcurses_LINK_LIBS})
            set(CURSES_CFLAGS ${ncurses_DEFINITIONS} ${ncurses_COMPILE_OPTIONS_C})
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
        # return
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
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
                if self.settings.compiler == "Visual Studio":
                    res += ".dll.lib"
                else:
                    res += ".dll.a"
        return res

    def package_id(self):
        self.info.options.with_ticlib = self._with_ticlib
        self.info.options.with_tinfo = self._with_tinfo

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Curses"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Curses"
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

        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["libcurses"].requires.extend([
                "getopt-for-visual-studio::getopt-for-visual-studio",
                "dirent::dirent",
            ])
            if self.options.get_safe("with_extended_colors", False):
                self.cpp_info.components["libcurses"].requires.append("naive-tsearch::naive-tsearch")

        module_rel_path = os.path.join(self._module_subfolder, self._module_file)
        self.cpp_info.components["libcurses"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["libcurses"].build_modules["cmake_find_package"] = [module_rel_path]
        self.cpp_info.components["libcurses"].build_modules["cmake_find_package_multi"] = [module_rel_path]

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

        terminfo = os.path.join(self.package_folder, "bin", "share", "terminfo")
        self.output.info("Setting TERMINFO environment variable: {}".format(terminfo))
        self.env_info.TERMINFO = terminfo

        self.user_info.lib_suffix = self._lib_suffix
