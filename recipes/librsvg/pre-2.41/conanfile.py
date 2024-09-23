import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, replace_in_file, save, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.54.0"


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
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

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
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("fontconfig/2.15.0")
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        self.requires("pango/1.54.0")
        self.requires("libxml2/[>=2.12.5 <3]")
        self.requires("gdk-pixbuf/2.42.10", transitive_headers=True, transitive_libs=True)
        self.requires("libcroco/0.6.13")

    def validate(self):
        if not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration("librsvg requires -o pango/*:with_cairo=True")
        if not self.dependencies["pango"].options.with_freetype:
            raise ConanInvalidConfiguration("librsvg requires -o pango/*:with_freetype=True")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")

        tc = AutotoolsToolchain(self)
        def yes_no(v): return "yes" if v else "no"
        tc.configure_args.extend([
            "--disable-gtk-doc",
            "--disable-introspection",  # fails to find Glib-2.0.gir without patching
            "--disable-pixbuf-loader",  # installed in a wrong location
            f"--enable-debug={yes_no(self.settings.build_type == 'Debug')}",
            f"--enable-tools={yes_no(self.options.tools)}",
        ])
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
            env.define("AR", f"{ar_wrapper} lib")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Force disable docs
        replace_in_file(self, os.path.join(self.source_folder, "configure.ac"),
                        "GTK_DOC_CHECK(", "# GTK_DOC_CHECK(")
        save(self, os.path.join(self.source_folder, "doc", "Makefile.am"), "")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "librsvg-2.0")
        self.cpp_info.set_property("pkg_config_custom_content", "svgz_supported=true\ncss_supported=true\n")
        self.cpp_info.includedirs.append(os.path.join("include", "librsvg-2.0"))
        self.cpp_info.libs = ["librsvg-2"]
        self.cpp_info.requires = [
            "cairo::cairo_",
            "cairo::cairo-png",
            "fontconfig::fontconfig",
            "gdk-pixbuf::gdk-pixbuf",
            "glib::gio-2.0",
            "glib::glib-2.0",
            "libxml2::libxml2",
            "pango::pangocairo",
            "pango::pangoft2",
            "libcroco::libcroco",
        ]
