from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


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
        "with_cxx": [True, False],
        "with_pcre2": [True, False],
        "with_reentrant": [True, False],
        "with_widec": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cxx": True,
        "with_pcre2": False,
        "with_reentrant": False,
        "with_widec": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.with_widec:
                raise ConanInvalidConfiguration("with_widec is unsupported for Visual Studio")
            raise ConanInvalidConfiguration("Unsupported on Visual Studio")
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_pcre2:
            self.requires("pcre2/10.33")

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("getopt-for-visual-studio/20200201")
            self.build_requires("dirent/1.23.2")
        if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ncurses-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        build = None
        host = None
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--with-shared", "--without-normal"])
        else:
            conf_args.extend(["--without-shared", "--with-normal"])
        if self.options.with_cxx:
            conf_args.append("--with-cxx-binding")
            if self.options.shared:
                conf_args.append("--with-cxx-shared")
            else:
                conf_args.append("--without-cxx-shared")
        else:
            conf_args.append("--without-cxx-binding")
        conf_args.extend([
            "--enable-reentrant" if self.options.with_reentrant else "--disable-reentrant",
            "--enable-widec" if self.options.with_widec else "--disable-widec",
            "--with-pcre2" if self.options.with_pcre2 else "--without-pcre2",
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
        ])
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
            self._autotools.defines.append("_WIN32")
            if self.settings.arch == "x86_64":
                self._autotools.defines.append("_WIN64")
            conf_args.extend([
                "ac_cv_func_getopt=yes",
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
                    "LDFLAGS": "user32.lib",
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
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make(target="libs" if self.settings.compiler == "Visual Studio" else None)

    @property
    def _major_version(self):
        return tools.Version(self.version).major

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            autotools.make(target="install.libs" if self.settings.compiler == "Visual Studio" else "install")

            os.unlink(os.path.join(self.package_folder, "bin", "ncurses{}{}-config".format(self._suffix, self._major_version)))

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

    @property
    def _libs(self):
        libs = []
        if self.options.with_cxx:
            libs.append("ncurses++")
        libs.extend(["form", "menu", "panel", "ncurses"])
        return list(l+self._lib_suffix for l in libs)

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "ncurses" + self._suffix))
        self.cpp_info.libs = self._libs
        if not self.options.shared:
            self.cpp_info.defines = ["NCURSES_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl", "m"]
