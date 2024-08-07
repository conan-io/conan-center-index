from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=1.53.0"

# some information taken from https://gitlab.gnome.org/GNOME/librsvg/-/blob/main/Cargo.toml
class LibrsvgConan(ConanFile):
    name = "librsvg"
    description = "A library to render SVG images to Cairo surfaces"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wiki.gnome.org/Projects/LibRsvg"
    topics = ("svg", "cairo")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "introspection": [True, False],
        "docs": [True, False],
        "vala": [True, False],
        "tests": [True, False],
        "pixbuf-loader": [True, False],
        "triplet": [False, "ANY"],
        "avif": [True, False],
        "rustc_version": [False, "ANY"],
        "with_gdk_pixbuf": [True, False],
        "with_gidocgen": [True, False],
        "with_introspection": [True, False],
        "with_vapigen": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "introspection": False,
        "docs": False,
        "vala": False,
        "tests": False,
        "pixbuf-loader": False,
        "triplet": False,
        "avif": True,
        "rustc_version": False,
        "with_gdk_pixbuf": False,
        "with_gidocgen": False,  # currently not on conancenter
        "with_introspection": False,
        "with_vapigen": False,
    }

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
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        self.requires("dav1d/1.3.0")
        self.requires("freetype/2.13.2")
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("harfbuzz/8.3.0")
        self.requires("libxml2/2.12.6")
        self.requires("pango/1.51.0")
        self.requires("fontconfig/2.15.0")

        if self.options.with_gdk_pixbuf:
            self.requires("gdk-pixbuf/2.42.10", transitive_headers=True, transitive_libs=True)
        if self.options.with_gidocgen:
            pass  # self.requires("...")
        if self.options.with_introspection:
            self.requires("gobject-introspection/1.72.0")
        if self.options.with_vapigen:
            pass  # self.requires("...")

    def validate(self):
        if self.options.with_gidocgen:
            raise ConanInvalidConfiguration("gidocgen recipe not available in conancenter yet")
        if self.options.with_vapigen:
            raise ConanInvalidConfiguration("vapigen recipe not available in conancenter yet")

        if is_msvc(self) and is_msvc_static_runtime(self) and not self.options.shared and \
           self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} static with MT runtime not supported if glib shared due to conancenter CI limitations"
            )

    def build_requirements(self):
        self.tool_requires("meson/[>1.2.0]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        # TODO add rustc

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        feature = lambda option: "enabled" if option else "disabled"
        true_false = lambda option: True if option else False

        tc = MesonToolchain(self)

        tc.project_options["introspection"] = feature(self.options.get_safe("introspection"))
        tc.project_options["docs"] = feature(self.options.get_safe("docs"))
        tc.project_options["vala"] = feature(self.options.get_safe("vala"))
        tc.project_options["tests"] = true_false(self.options.get_safe("tests"))
        tc.project_options["avif"] = feature(self.options.get_safe("avif"))
        tc.project_options["pixbuf"] = feature(self.options.with_gdk_pixbuf)
        tc.project_options["pixbuf-loader"] = feature(self.options.get_safe("pixbuf-loader"))
        if self.options.get_safe("triplet"):
            tc.project_options["triplet"] = self.options.get_safe("triplet")
        if self.options.get_safe("rustc_version"):
            tc.project_options["rustc-version"] = self.options.get_safe("rustc_version")
        tc.generate()
        
        
        tc = PkgConfigDeps(self)
        tc.generate()

        tc = VirtualBuildEnv(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING.LIB", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.libs = ["rsvg-2"]
        self.cpp_info.includedirs += [
            os.path.join("include", "librsvg-2.0"),
        ]

        self.cpp_info.requires = [
            "cairo::cairo_",
            "cairo::cairo-png",
            "cairo::cairo-gobject",
            "fontconfig::fontconfig",
            "freetype::freetype",
            "glib::gio-2.0",
            "glib::glib-2.0",
            "glib::gobject-2.0",
            "harfbuzz::harfbuzz",
            "libxml2::libxml2",
            "pango::pangocairo",
            "pango::pangoft2",
            "dav1d::dav1d",
        ]

        self.cpp_info.set_property("pkg_config_name", "librsvg-2.0")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
        
        # this is a somewhat temporary fix for rust, should probably be handled by a rust recipe
        if is_msvc(self):
            self.cpp_info.system_libs += ["ntdll", "userenv.lib"]

        if self.options.with_gdk_pixbuf:
            self.cpp_info.requires += ["gdk-pixbuf::gdk-pixbuf"]
        if self.options.with_gidocgen:
            pass  # currently not present on conan-center
        if self.options.with_introspection:
            pass  # self.cpp_info.requires.append()
            # unsure about this, package seems to be broken anyway
        if self.options.with_vapigen:
            pass  # currently not present on conan-center

# stolen from the libvips recipe
def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib in case of cl like compiler"""
    from conan.tools.files import rename
    import glob
    if not conanfile.settings.get_safe("compiler.runtime"):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
