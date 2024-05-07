from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

#
# INFO: Please, remove all comments before pushing your PR!
#

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

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self, src_folder="src")

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        self.requires("cairo/1.18.0")
        self.requires("dav1d/1.3.0")
        self.requires("freetype/2.13.2")
        self.requires("glib/2.78.3")  # I think this includes gio?
        self.requires("harfbuzz/8.3.0")
        self.requires("libxml2/2.12.6")
        self.requires("pango/1.51.0")

        if self.options.with_gdk_pixbuf:
            self.requires("gdk-pixbuf/2.42.10")
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

    # if another tool than the compiler or Meson is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        # CCI policy assumes that Meson may not be installed on consumers machine
        self.tool_requires("meson/[>1.2.0]")
        # pkgconf is largely used by Meson, it should be added in build requirement when there are dependencies
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # Meson feature options must be set to "enabled" or "disabled"
        feature = lambda option: "enabled" if option else "disabled"
        true_false = lambda option: True if option else False

        # default_library and b_staticpic are automatically parsed when self.options.shared and self.options.fpic exist
        # buildtype is automatically parsed for self.settings
        tc = MesonToolchain(self)

        # Meson features are typically enabled automatically when possible.
        # The default behavior can be changed to disable all features by setting "auto_features" to "disabled".
        # tc.project_options["auto_features"] = "disabled"
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

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        # In shared lib/executable files, meson set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["librsvg"]
        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "librsvg-2")
        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])

        if self.options.with_gdk_pixbuf:
            self.cpp_info.components["librsvg"].requires.append("gdk-pixbuf::gdk-pixbuf")
        if self.options.with_gidocgen:
            pass
        if self.options.with_introspection:
            pass  # self.cpp_info.components["librsvg"].requires.append()
            # unsure about this, package seems to be broken anyway
        if self.options.with_vapigen:
            pass
