from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import (
    copy,
    get,
    replace_in_file,
    rm,
    rmdir
)
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class GobjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    description = "GObject introspection is a middleware layer between C libraries (using GObject) and language bindings"
    topics = ("conan", "gobject-instrospection")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/gobject-introspection"
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def build_requirements(self):
        if Version(self.version) >= "1.71.0":
            self.tool_requires("meson/0.64.1")
        else:
            # https://gitlab.gnome.org/GNOME/gobject-introspection/-/issues/414
            self.tool_requires("meson/0.59.3")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.7.6")

    def requirements(self):
        self.requires("glib/2.75.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        PkgConfigDeps(self).generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "build_introspection_data": False
        })
        tc.generate()

        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('tests')", "#subdir('tests')")
        if Version(self.version) <= "1.72.0":
            replace_in_file(
                self,
                os.path.join(self.source_folder, "meson.build"),
                "if meson.version().version_compare('>=0.54.0')",
                "if false"
            )

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if is_msvc(self):
            rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gobject-introspection-1.0")
        self.cpp_info.names["pkg_config"] = "gobject-introspection-1.0"
        self.cpp_info.libs = ["girepository-1.0"]
        self.cpp_info.includedirs.append(
            os.path.join("include", "gobject-introspection-1.0")
        )

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.buildenv_info.append_path("PATH", bin_path)
        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(bin_path)

        exe_ext = ".exe" if self.settings.os == "Windows" else ""

        pkgconfig_variables = {
            'datadir': '${prefix}/res',
            'bindir': '${prefix}/bin',
            'g_ir_scanner': '${bindir}/g-ir-scanner',
            'g_ir_compiler': '${bindir}/g-ir-compiler%s' % exe_ext,
            'g_ir_generate': '${bindir}/g-ir-generate%s' % exe_ext,
            'gidatadir': '${datadir}/gobject-introspection-1.0',
            'girdir': '${datadir}/gir-1.0',
            'typelibdir': '${libdir}/girepository-1.0',
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join("%s=%s" % (key, value) for key,value in pkgconfig_variables.items()))
