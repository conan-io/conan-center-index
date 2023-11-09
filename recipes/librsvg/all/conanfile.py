import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.53.0"

class LibrsvgConan(ConanFile):
    name = "librsvg"
    description = "A library to render SVG images to Cairo surfaces."
    license = "LGPL-2.0-or-later"
    homepage = "https://gitlab.gnome.org/GNOME/librsvg"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("svg", "vector-graphics", "cairo", "gnome")

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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        pass

    def requirements(self):
        # https://gitlab.gnome.org/GNOME/librsvg/-/blob/main/ci/build-dependencies.sh#L5-13
        # All public includes are located here:
        # https://gitlab.gnome.org/GNOME/librsvg/-/blob/2.57.0/include/librsvg/rsvg.h#L30-34
        self.requires("glib/2.78.1", transitive_headers=True, transitive_libs=True, force=True)
        # self.requires("gobject-introspection/1.78.0")
        self.requires("freetype/2.13.0")
        self.requires("fontconfig/2.14.2")
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        self.requires("harfbuzz/8.2.2")
        self.requires("pango/1.51.0")
        self.requires("libxml2/2.11.5")
        self.requires("gdk-pixbuf/2.42.10", transitive_headers=True, transitive_libs=True)

    def validate(self):
        pass

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
        self.tool_requires("rust/1.73.0")
        self.tool_requires("gdk-pixbuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--disable-gtk-doc",
            f"--enable-debug={yes_no(self.settings.build_type == 'Debug')}",
            # TODO: introspection can be enabled once gobject-introspection is available
            "--disable-introspection",
        ]
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

        if is_msvc(self):
            env = Environment()
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

    def _patch_sources(self):
        # Fix freetype version check, which uses a different versioning format
        replace_in_file(self, os.path.join(self.source_folder, "configure"), "20.0.14", "2.8")
        replace_in_file(self, os.path.join(self.source_folder, "rsvg", "Cargo.toml"), "20.0.14", "2.8")
        # Disable building of rsvg_convert executable and installation of non-essential files
        # Also, rsvg_convert failed to link with libpango-c8d4953be534d8af.rlib: undefined reference to `pango_attr_overline_new'
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"), "$(EXTRA_DIST)", "$(LIBRSVG_SRC)")
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"), "bin_SCRIPTS =", "bin_SCRIPTS = #")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING.LIB", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "gdk-pixbuf-2.0"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "librsvg-2.0")
        self.cpp_info.includedirs.append(os.path.join("include", "librsvg-2.0"))
        self.cpp_info.libs = ["librsvg-2"]

        # https://gitlab.gnome.org/GNOME/librsvg/-/blob/2.57.0/configure.ac#L161-173
        self.cpp_info.requires = [
            "cairo::cairo_",
            "cairo::cairo-png",
            "cairo::cairo-gobject",
            "fontconfig::fontconfig",
            "freetype::freetype",
            "gdk-pixbuf::gdk-pixbuf",
            "glib::gio-2.0",
            "glib::glib-2.0",
            "harfbuzz::harfbuzz",
            "libxml2::libxml2",
            "pango::pangocairo",
            "pango::pangoft2",
        ]
