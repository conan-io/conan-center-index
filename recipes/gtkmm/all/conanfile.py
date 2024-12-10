import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class GtkmmConan(ConanFile):
    name = "gtkmm"
    description = "gtkmm is a C++ wrapper for GTK, a library used to create graphical user interfaces."
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/gtkmm"
    topics = "gtk", "wrapper", "gui", "widgets", "gnome"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_atkmm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_atkmm": False,  # TODO: enable when atkmm is available
    }
    implements = ["auto_shared_fpic"]

    @property
    def _is_gtk4(self):
        return Version(self.version).major == 4

    @property
    def _abi_version(self):
        return "4.0" if Version(self.version).major == 4 else "3.0"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self._is_gtk4:
            del self.options.with_atkmm

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self._is_gtk4:
            self.requires("gtk/4.15.6", transitive_headers=True, transitive_libs=True)
            self.requires("glibmm/2.78.1", transitive_headers=True, transitive_libs=True)
            self.requires("cairomm/1.18.0", transitive_headers=True, transitive_libs=True)
            self.requires("pangomm/2.54.0", transitive_headers=True, transitive_libs=True)
            self.requires("libsigcpp/3.0.7", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("gtk/3.24.43", transitive_headers=True, transitive_libs=True)
            self.requires("glibmm/2.66.4", transitive_headers=True, transitive_libs=True)
            self.requires("cairomm/1.14.5", transitive_headers=True, transitive_libs=True)
            self.requires("pangomm/2.46.4", transitive_headers=True, transitive_libs=True)
            self.requires("libsigcpp/2.10.8", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.get_safe("with_atkmm"):
            raise ConanInvalidConfiguration("atkmm is not yet available on CCI")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["build-demos"] = "false"
        tc.project_options["build-tests"] = "false"
        tc.project_options["msvc14x-parallel-installable"] = "false"
        if not self._is_gtk4:
            tc.project_options["build-atkmm-api"] = "true" if self.options.get_safe("with_atkmm") else "false"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)
        if is_msvc(self) and not self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", f"libgtkmm-{self._abi_version}.a"),
                         os.path.join(self.package_folder, "lib", f"gtkmm-{self._abi_version}.lib"))

    def package_info(self):
        if not self._is_gtk4:
            gdkmm_lib = f"gdkmm-{self._abi_version}"
            self.cpp_info.components[gdkmm_lib].set_property("pkg_config_name", gdkmm_lib)
            self.cpp_info.components[gdkmm_lib].libs = [gdkmm_lib]
            self.cpp_info.components[gdkmm_lib].includedirs += [
                os.path.join("include", gdkmm_lib),
                os.path.join("lib", gdkmm_lib, "include")
            ]
            self.cpp_info.components[gdkmm_lib].requires = [
                "gtk::gtk+-3.0",
                "glibmm::giomm-2.4",
                "cairomm::cairomm-1.0",
                "pangomm::pangomm-1.4",
                "libsigcpp::libsigcpp"
            ]

        gtkmm_lib = f"gtkmm-{self._abi_version}"
        self.cpp_info.components[gtkmm_lib].set_property("pkg_config_name", gtkmm_lib)
        self.cpp_info.components[gtkmm_lib].set_property("pkg_config_custom_content", "gmmprocm4dir=${libdir}/%s/proc/m4" % gtkmm_lib)
        self.cpp_info.components[gtkmm_lib].libs = [gtkmm_lib]
        self.cpp_info.components[gtkmm_lib].includedirs += [
            os.path.join("include", gtkmm_lib),
            os.path.join("lib", gtkmm_lib, "include")
        ]
        if self._is_gtk4:
            self.cpp_info.components[gtkmm_lib].requires = [
                "gtk::gtk4",
                "glibmm::giomm-2.68",
                "cairomm::cairomm-1.16",
                "pangomm::pangomm-2.48",
                "libsigcpp::libsigcpp"
            ]
            if self.settings.os != "Windows":
                self.cpp_info.components[gtkmm_lib].requires.append("gtk::gtk4-unix-print")
        else:
            self.cpp_info.components[gtkmm_lib].requires = [gdkmm_lib]
            if self.options.get_safe("with_atkmm"):
                self.cpp_info.components[gtkmm_lib].requires.append("atkmm::atkmm-1.6")
            if self.settings.os != "Windows":
                self.cpp_info.components[gtkmm_lib].requires.append("gtk::gtk+-unix-print-3.0")
