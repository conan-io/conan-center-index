import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration


class ReadLineConan(ConanFile):
    name = "readline"
    description = "A set of functions for use by applications that allow users to edit command lines as they are typed in"
    topics = ("cli", "terminal", "command")
    license = "GPL-3.0-only"
    homepage = "https://tiswww.case.edu/php/chet/readline/rltop.html"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_library": ["termcap", "curses"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_library": "termcap",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_library == "termcap":
            self.requires("termcap/1.3.1")
        elif self.options.with_library == "curses":
            self.requires("ncurses/6.2")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("readline does not support Visual Studio")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        configure_args = [
            "--with-curses={}".format("yes" if self.options.with_library == "curses" else "no"),
        ]
        if self.options.shared:
            configure_args.extend(["--enable-shared", "--disable-static"])
        else:
            configure_args.extend(["--enable-static", "--disable-shared"])
        if tools.cross_building(self.settings):
            configure_args.append("bash_cv_wcwidth_broken=yes")

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # this should be really done automatically by the AutoToolsBuildEnvironment helper,
            # but very unlikely old helper will be fixed any time soon
            self._autotools.link_flags.extend(["-arch", "arm64"])
        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "shlib", "Makefile.in"), "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS)",
                              "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS) -ltermcap")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"), "@TERMCAP_LIB@", "-ltermcap")

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["history", "readline"]
