import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.env import Environment
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.scm import Version

required_conan_version = ">2.1"


class GobjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    description = ("GObject introspection is a middleware layer between "
                   "C libraries (using GObject) and language bindings")
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/gobject-introspection"
    topics = ("gobject-instrospection",)

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "build_introspection_data": [True, False],
    }
    default_options = {
        "fPIC": True,
        "build_introspection_data": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ["Windows", "Macos"] or cross_building(self):
            # FIXME: tools/g-ir-scanner fails to load glib
            self.options.build_introspection_data = False

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # https://gitlab.gnome.org/GNOME/gobject-introspection/-/blob/1.86.0/meson.build?ref_type=tags#L156
        self.requires("glib/[>=2.78.3 <3]", transitive_headers=True, transitive_libs=True)
        # ffi.h is exposed by public header gobject-introspection-1.0/girffi.h
        self.requires("libffi/[>=3.4.4 <4]", transitive_headers=True)

    def validate(self):
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            # fatal error LNK1104: cannot open file 'python37_d.lib'
            raise ConanInvalidConfiguration(
                f"{self.ref} debug build on Windows is disabled due to debug version of Python libs likely not being available. Contributions to fix this are welcome.")
        if self.options.build_introspection_data and self.settings.os in ["Windows", "Macos"]:
            # FIXME: tools/g-ir-scanner', '--output=gir/GLib-2.0.gir' ... ERROR: can't resolve libraries to shared libraries: glib-2.0, gobject-2.0
            # FIXME: g-ir-scanner fails to find libgnuintl
            # giscanner/_giscanner.cpython-37m-darwin.so, 0x0002): Library not loaded: /lib/libgnuintl.8.dylib
            raise ConanInvalidConfiguration(f"{self.ref} build_introspection_data is not supported on {self.settings.os}. Use '&:build_introspection_data=False'. Contributions to fix this are welcome.")
        if self.options.build_introspection_data and cross_building(self):
            raise ConanInvalidConfiguration(f"{self.ref} build_introspection_data is not supported when cross-building. Use '&:build_introspection_data=False'.")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.4 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")
        self.tool_requires("glib/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        if cross_building(self):
            tc.project_options["gi_cross_use_prebuilt_gi"] = "false"
        tc.project_options["build_introspection_data"] = bool(self.options.build_introspection_data)
        tc.project_options["datadir"] = "res"
        if Version(self.version) >= "1.86.0":
            tc.project_options["tests"] = False
        tc.generate()
        deps = PkgConfigDeps(self)
        # INFO: glib tools need to load glib shared libraries at runtime, point their pkg-config bindir to the build context binary directory
        glib_build_context_bindir = self.dependencies.build["glib"].cpp_info.bindirs[0]
        for component in ("glib-2.0", "gio-2.0"):
            glib_pkg_config_vars = self.dependencies.host["glib"].cpp_info.components[component].get_property("pkg_config_custom_content", None)
            if glib_pkg_config_vars:
                deps.set_property(f"glib::{component}", "pkg_config_custom_content", glib_pkg_config_vars.replace("${bindir}", glib_build_context_bindir))
        deps.generate()
        # INFO: g-ir-scanner uses PKG_CONFIG_PATH directly instead of pkg-config Meson module
        env = Environment()
        env.define_path("PKG_CONFIG_PATH", self.generators_folder)
        # INFO: g-ir-scanner uses the compiler from CC/CXX, otherwise the one Python was built with
        compilers = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        if compilers.get("c"):
            env.define("CC", compilers["c"])
        if compilers.get("cpp"):
            env.define("CXX", compilers["cpp"])
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
        if Version(self.version) >= "1.86.0" and self.settings.os != "Windows":
            # Avoid using absolute Python path for installed scripts
            replace_in_file(self, os.path.join(self.source_folder, "tools", "meson.build"),
                            "if not python.full_path().startswith('/usr/bin')",
                            "if false")
        if Version(self.version) >= "1.86.0" and not self.options.build_introspection_data:
            # Avoid setuptools when build_introspection_data is disabled - checked by g-ir-scanner setup
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            "get_option('python'), modules: ['setuptools'])",
                            "get_option('python'))")
        if Version(self.version) < "1.86.0":
            # INFO: setuptools distutils has no msvccompiler module, use compiler_type like 1.86.0 does
            ccompiler_py = os.path.join(self.source_folder, "giscanner", "ccompiler.py")
            replace_in_file(self, ccompiler_py, "from distutils.msvccompiler import MSVCCompiler\n", "")
            replace_in_file(self, ccompiler_py, "return isinstance(self.compiler, MSVCCompiler)", "return self.compiler.compiler_type == \"msvc\"")
            replace_in_file(self, ccompiler_py, "if isinstance(self.compiler, MSVCCompiler):", "if self.check_is_msvc():")
        if self.options.build_introspection_data:
            # INFO: Static libraries (e.g. glib) are not listed by ldd, do not abort g-ir-scanner when they are not resolved
            replace_in_file(self, os.path.join(self.source_folder, "giscanner", "shlibs.py"),
                            '''        raise SystemExit(
            "ERROR: can't resolve libraries to shared libraries: " +
            ", ".join(patterns.keys()))''',
                            '''        sys.stderr.write(
            "WARNING: can't resolve libraries to shared libraries: " +
            ", ".join(patterns.keys()) + "\\n")''')

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
        self.cpp_info.set_property("pkg_config_name", "gobject-introspection-1.0")
        self.cpp_info.libs = ["girepository-1.0"]
        self.cpp_info.includedirs.append(os.path.join("include", "gobject-introspection-1.0"))

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
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()),
        )
        self.buildenv_info.define_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
        self.buildenv_info.define_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))
