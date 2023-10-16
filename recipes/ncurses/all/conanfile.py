from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class NCursesConan(ConanFile):
    name = "ncurses"
    description = "The ncurses (new curses) library is a free software emulation of curses in System V Release 4.0 (SVr4), and more"
    license = "X11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/ncurses"
    topics = ("terminal", "screen", "tui")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "*.cmake", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.with_ticlib == "auto":
            self.options.with_ticlib = self.settings.os != "Windows"
        if self.options.with_tinfo == "auto":
            self.options.with_tinfo = self.settings.os != "Windows"

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
            self.requires("dirent/1.24")
            if self.options.get_safe("with_extended_colors", False):
                self.requires("naive-tsearch/0.1.1")

    def validate(self):
        if cross_building(self) and ("arm" in self.settings.arch or "arm" in self._settings_build.arch):
            # FIXME: Cannot build ncurses from x86_64 to armv8 (Apple M1).  Cross building from Linux/x86_64 to Mingw/x86_64 works flawless.
            # FIXME: Need access to environment of build profile to set build compiler (BUILD_CC/CC_FOR_BUILD)
            raise ConanInvalidConfiguration("Cross building to/from arm is (currently) not supported")
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Cannot build shared libraries with static (MT) runtime")
        if self.settings.os == "Windows":
            if self.options.with_tinfo:
                raise ConanInvalidConfiguration("terminfo cannot be built on Windows because it requires a term driver")
            if self.options.shared and self.options.with_ticlib:
                raise ConanInvalidConfiguration("ticlib cannot be built separately as a shared library on Windows")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--with-shared={}".format(yes_no(self.options.shared)),
            "--with-cxx-shared={}".format(yes_no(self.options.shared)),
            "--with-normal={}".format(yes_no(not self.options.shared)),
            "--enable-widec={}".format(yes_no(self.options.with_widec)),
            "--enable-ext-colors={}".format(yes_no(self.options.get_safe("with_extended_colors", False))),
            "--enable-reentrant={}".format(yes_no(self.options.with_reentrant)),
            "--with-pcre2={}".format(yes_no(self.options.with_pcre2)),
            "--with-cxx-binding={}".format(yes_no(self.options.with_cxx)),
            "--with-progs={}".format(yes_no(self.options.with_progs)),
            "--with-termlib={}".format(yes_no(self.options.with_tinfo)),
            "--with-ticlib={}".format(yes_no(self.options.with_ticlib)),
            "--without-libtool",
            "--without-ada",
            "--without-manpages",
            "--without-tests",
            "--disable-echo",
            "--without-debug",
            "--without-profile",
            "--with-sp-funcs",
            "--disable-rpath",
            "--datarootdir=${prefix}/res",
            "--disable-pc-files",
        ]
        build = None
        host = None
        if self.settings.os == "Windows":
            tc.configure_args += [
                "--disable-macros",
                "--disable-termcap",
                "--enable-database",
                "--enable-sp-funcs",
                "--enable-term-driver",
                "--enable-interop",
            ]
        if is_msvc(self):
            build = host = f"{self.settings.arch}-w64-mingw32-msvc"
            tc.configure_args.extend([
                "ac_cv_func_getopt=yes",
                "ac_cv_func_setvbuf_reversed=no",
            ])
            tc.extra_cxxflags.append("-EHsc")
            if Version(self.settings.compiler.version) >= 12:
                tc.extra_cxxflags.append("-FS")
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

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
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

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        os.unlink(os.path.join(self.package_folder, "bin", f"ncurses{self._suffix}{self._major_version}-config"))
        copy(self, "*.cmake",
             src=os.path.join(self.export_sources_folder, "cmake"),
             dst=os.path.join(self.package_folder, self._module_subfolder))

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
        return f"conan-official-{self.name}-targets.cmake"

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Curses")
        # CMake's standard FindCurses module does not define a target.
        # Adding one nevertheless for consistency with other packages.
        self.cpp_info.set_property("cmake_target_name", "Curses::Curses")

        def _add_component(name, lib_name=None, requires=None):
            lib_name = lib_name or name
            self.cpp_info.components[name].libs = [lib_name + self._lib_suffix]
            self.cpp_info.components[name].set_property("pkg_config_name", lib_name + self._lib_suffix)
            self.cpp_info.components[name].includedirs.append(os.path.join("include", "ncurses" + self._suffix))
            self.cpp_info.components[name].requires = requires if requires else []

        _add_component("libcurses", lib_name="ncurses")
        _add_component("panel", requires=["libcurses"])
        _add_component("menu", requires=["libcurses"])
        _add_component("form", requires=["libcurses"])
        if self.options.with_tinfo:
            _add_component("tinfo")
            self.cpp_info.components["libcurses"].requires += ["tinfo"]
        if self.options.with_cxx:
            _add_component("curses++", lib_name="ncurses++", requires=["libcurses"])
        if self.options.with_ticlib:
            _add_component("ticlib", lib_name="tic", requires=["libcurses"])

        if is_msvc(self):
            self.cpp_info.components["libcurses"].requires += [
                "getopt-for-visual-studio::getopt-for-visual-studio",
                "dirent::dirent",
            ]
            if self.options.get_safe("with_extended_colors"):
                self.cpp_info.components["libcurses"].requires += [
                    "naive-tsearch::naive-tsearch"
                ]
        if self.options.with_pcre2:
            self.cpp_info.components["form"].requires.append("pcre2::pcre2")

        if not self.options.shared:
            self.cpp_info.components["libcurses"].defines = ["NCURSES_STATIC"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libcurses"].system_libs = ["dl", "m"]

        module_rel_path = os.path.join(self._module_subfolder, self._module_file)
        self.cpp_info.components["libcurses"].builddirs.append(self._module_subfolder)
        self.cpp_info.set_property("cmake_build_modules", [module_rel_path])

        terminfo = os.path.join(self.package_folder, "res", "terminfo")
        self.buildenv_info.define_path("TERMINFO", terminfo)
        self.runenv_info.define_path("TERMINFO", terminfo)
        self.conf_info.define("user.ncurses:lib_suffix", self._lib_suffix)

        # TODO: Legacy, to be removed on Conan 2.0
        self.cpp_info.filenames["cmake_find_package"] = "Curses"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Curses"
        self.cpp_info.components["libcurses"].build_modules["cmake_find_package"] = [module_rel_path]
        self.cpp_info.components["libcurses"].build_modules["cmake_find_package_multi"] = [module_rel_path]
        if self.options.with_progs:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
        self.output.info(f"Setting TERMINFO environment variable: {terminfo}")
        self.env_info.TERMINFO = terminfo
        self.user_info.lib_suffix = self._lib_suffix
