import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=2.1"


class LibgsfConan(ConanFile):
    name = "libgsf"
    description = "The G Structured File Library"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/libgsf"
    topics = ("gnome", "structured-file", "ole2", "zip", "compound-document")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # INFO: gsf/gsf-fwd.h includes glib-object.h
        self.requires("glib/2.81.0", transitive_headers=True, transitive_libs=True)
        # INFO: gsf/gsf-libxml.h includes libxml/parser.h
        self.requires("libxml2/[>=2.12.5 <3]", transitive_headers=True, transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]")

    def build_requirements(self):
        # upstream configure.ac relies on PKG_CHECK_MODULES
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        # zlib is looked up by hand instead of pkg-config
        zlib_root = unix_path(self, self.dependencies["zlib"].package_folder)
        tc.configure_args.extend([
            f"--with-zlib={zlib_root}",
            "--without-bz2",
            "--without-gdk-pixbuf",
            "--disable-introspection",
            "--disable-gtk-doc",
            "--disable-nls",
        ])
        tc.generate()

        PkgConfigDeps(self).generate()

        if is_msvc(self):
            env = Environment()
            # get compile & ar-lib from automake to wrap cl and lib
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["gsf-1"]
        self.cpp_info.includedirs = [os.path.join("include", "libgsf-1")]
        self.cpp_info.set_property("pkg_config_name", "libgsf-1")
