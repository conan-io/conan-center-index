import os
from conan import ConanFile
from conan.tools.files import get, replace_in_file, rmdir
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.gnu import AutotoolsToolchain, Autotools
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
        del self.settings.compiler.cppstd

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("readline does not support Visual Studio")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--with-curses={}".format("yes" if self.options.with_library == "curses" else "no"),
        ])
        if self.options.shared:
            tc.configure_args.extend(["--enable-shared", "--disable-static"])
        else:
            tc.configure_args.extend(["--enable-static", "--disable-shared"])
        if cross_building(self.settings):
            tc.configure_args.append("bash_cv_wcwidth_broken=yes")
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "shlib", "Makefile.in"), "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS)",
                              "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS) -ltermcap")
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"), "@TERMCAP_LIB@", "-ltermcap")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["history", "readline"]
