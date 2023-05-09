import os
from conan import ConanFile
from conan.tools.files import get, replace_in_file, rmdir, copy
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.env import VirtualRunEnv
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"

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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("readline does not support Visual Studio")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            # Expose LD_LIBRARY_PATH when there are shared dependencies,
            # as configure tries to run a test executable (when not cross-building)
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--with-curses={}".format("yes" if self.options.with_library == "curses" else "no"),
        ])
        if cross_building(self):
            tc.configure_args.append("bash_cv_wcwidth_broken=yes")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "shlib", "Makefile.in"), "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS)",
                              "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS) -ltermcap")
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"), "@TERMCAP_LIB@", "-ltermcap")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["history", "readline"]
