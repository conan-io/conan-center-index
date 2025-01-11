import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.env import Environment
from conan.tools.apple import fix_apple_shared_install_name

required_conan_version = ">=2.4"


class GobjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    description = ("GObject introspection is a middleware layer between "
                   "C libraries (using GObject) and language bindings")
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/gobject-introspection"
    topics = ("gobject-instrospection",)

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "build_introspection_data": [True, False],
    }
    default_options = {
        "build_introspection_data": True,
    }
    short_paths = True
    languages = ["C"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings_target is not None:
            # Building gobject-introspection as a tool_requires.
            # Build only the tools by default.
            self.options.build_introspection_data = False
        if self.settings.os in ["Windows", "Macos"]:
            # FIXME: tools/g-ir-scanner fails to load glib
            self.options.build_introspection_data = False

    def configure(self):
        if self.options.get_safe("build_introspection_data"):
            # INFO: g-ir-scanner looks for dynamic glib and gobject libraries when running
            self.options["glib"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # https://gitlab.gnome.org/GNOME/gobject-introspection/-/blob/1.76.1/meson.build?ref_type=tags#L127-131
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        # ffi.h is exposed by public header gobject-introspection-1.0/girffi.h
        self.requires("libffi/3.4.4", transitive_headers=True)

    def validate(self):
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            # fatal error LNK1104: cannot open file 'python37_d.lib'
            raise ConanInvalidConfiguration(
                f"{self.ref} debug build on Windows is disabled due to debug version of Python libs likely not being available. Contributions to fix this are welcome.")
        if self.options.build_introspection_data and not self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration("Built introspection data requires shared GLib. Use -o 'glib/*:shared=True'.")
        if self.options.build_introspection_data and self.settings.os in ["Windows", "Macos"]:
            # FIXME: tools/g-ir-scanner', '--output=gir/GLib-2.0.gir' ... ERROR: can't resolve libraries to shared libraries: glib-2.0, gobject-2.0
            # FIXME: g-ir-scanner fails to find libgnuintl
            # giscanner/_giscanner.cpython-37m-darwin.so, 0x0002): Library not loaded: /lib/libgnuintl.8.dylib
            raise ConanInvalidConfiguration(f"{self.ref} fails to run g-ir-scanner due glib loaded as shared. Use -o 'glib/*:shared=False'. Contributions to fix this are welcome.")
        if self.options.build_introspection_data and cross_building(self):
            # Cross-compilation of introspection data requires an exe_wrapper like QEMU.
            raise ConanInvalidConfiguration("build_introspection_data is not supported when cross-building."
                                            f" Use '-o gobject-introspection/*:build_introspection_data=False' if it's not needed.")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")
        self.tool_requires("glib/<host_version>")
        self.requires("cpython/[~3.12]", build=True, visible=True, run=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = MesonToolchain(self)
        if cross_building(self):
            tc.project_options["gi_cross_use_prebuilt_gi"] = "false"
        tc.project_options["build_introspection_data"] = self.options.build_introspection_data
        tc.project_options["datadir"] = "res"
        tc.project_options["cairo"] = "disabled"  # only used for tests
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()
        # INFO: g-ir-scanner uses PKG_CONFIG_PATH directly instead of pkg-config Meson module
        env = Environment()
        env.define_path("PKG_CONFIG_PATH", self.generators_folder)
        envvars = env.vars(self)
        envvars.save_script("pkg_config_env")

    def _patch_sources(self):
        # Disable tests
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                        "subdir('tests')",
                        "#subdir('tests')")
         # Look for data files in res/ instead of share/
        replace_in_file(self, os.path.join(self.source_folder, "tools", "g-ir-tool-template.in"),
                        "os.path.join(filedir, '..', 'share')",
                        "os.path.join(filedir, '..', 'res')")
        # gir/meson.build expects the gio-unix-2.0 includedir to be passed as a build flag.
        # Patch this for glib from Conan.
        replace_in_file(self, os.path.join(self.source_folder, "gir", "meson.build"),
                        "join_paths(giounix_dep.get_variable(pkgconfig: 'includedir'), 'gio-unix-2.0')",
                        "giounix_dep.get_variable(pkgconfig: 'includedir')")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        component = self.cpp_info.components["gobject-introspection-1.0"]
        component.set_property("pkg_config_name", "gobject-introspection-1.0")
        component.libs = ["girepository-1.0"]
        component.includedirs = [os.path.join("include", "gobject-introspection-1.0")]
        component.requires = [
            "glib::glib-2.0",
            "glib::gobject-2.0",
            "glib::gio-2.0",
            "libffi::libffi",
        ]

        exe_ext = ".exe" if self.settings.os == "Windows" else ""
        pkgconfig_variables = {
            "datadir": "${prefix}/res",
            "bindir": "${prefix}/bin",
            "libdir": "${prefix}/lib",
            "g_ir_scanner": "${bindir}/g-ir-scanner",
            "g_ir_compiler": "${bindir}/g-ir-compiler%s" % exe_ext,
            "g_ir_generate": "${bindir}/g-ir-generate%s" % exe_ext,
            "gidatadir": "${datadir}/gobject-introspection-1.0",
            "girdir": "${datadir}/gir-1.0",
            "typelibdir": "${libdir}/girepository-1.0",
        }
        component.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()),
        )

        if self.options.build_introspection_data:
            self.buildenv_info.define_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
            self.runenv_info.define_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))
