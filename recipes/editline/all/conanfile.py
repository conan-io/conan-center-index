from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class EditlineConan(ConanFile):
    name = "editline"
    description = "Autotool- and libtoolized port of the NetBSD Editline library (libedit)."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://thrysoee.dk/editline/"
    topics = ("libedit", "line", "editing", "history", "tokenization")
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "terminal_db": ["termcap", "ncurses", "tinfo"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "terminal_db": "termcap",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.terminal_db == "termcap":
            self.requires("termcap/1.3.1")
        elif self.options.terminal_db == "ncurses":
            self.requires("ncurses/6.4")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by libedit (missing termios.h)")
        if self.options.terminal_db == "tinfo":
            # TODO - Add tinfo when available
            raise ConanInvalidConfiguration("tinfo is not (yet) available on CCI")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-examples")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libedit")
        self.cpp_info.libs = ["edit"]
        self.cpp_info.includedirs.append(os.path.join("include", "editline"))
