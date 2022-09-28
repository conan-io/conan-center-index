import functools
import os

from conan import ConanFile
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.gnu import PkgConfigDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools import files, microsoft, scm
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.52.0"


class LibnameConan(ConanFile):
    name = "graphene"
    description = "A thin layer of graphic data types."
    topics = ("graphic", "canvas", "types")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ebassi.github.io/graphene/"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_glib": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_glib": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "gcc":
            if tools.Version(self.settings.compiler.version) < "5.0":
                raise ConanInvalidConfiguration("graphene does not support GCC before 5.0")

    def build_requirements(self):
        self.build_requires("meson/0.63.2")
        self.build_requires("pkgconf/1.9.3")

    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.74.0")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared and self.options.with_glib:
            self.options["glib"].shared = True

    def validate(self):
        if self.options.shared and self.options.with_glib and not self.options["glib"].shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )

    def layout(self):
        basic_layout(self, src_folder="source")

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()

        meson = MesonToolchain(self)
        meson.project_options.update({
            "tests": "false",
            "installed_tests": "false",
            "gtk_doc": "false"
        })
        meson.project_options["gobject_types"] = "true" if self.options.with_glib else "false"
        if scm.Version(self.version) < "1.10.4":
            meson.project_options["introspection"] = "false"
        else:
            meson.project_options["introspection"] = "disabled"
        meson.generate()

        venv = VirtualBuildEnv(self)
        venv.generate()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        meson.configure()
        return meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        meson = self._configure_meson()
        meson.install()
        files.copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))

        if microsoft.is_msvc(self) and not self.options.shared:
            libfolder = os.path.join(self.package_folder, "lib")
            files.rename(self, os.path.join(libfolder, "libgraphene-1.0.a"), os.path.join(libfolder, "graphene-1.0.lib"))

        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.components["graphene-1.0"].set_property("pkg_config_name", "graphene-1.0")
        self.cpp_info.components["graphene-1.0"].libs = ["graphene-1.0"]
        self.cpp_info.components["graphene-1.0"].includedirs = [os.path.join("include", "graphene-1.0"), os.path.join("lib", "graphene-1.0", "include")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["graphene-1.0"].system_libs = ["m", "pthread"]
        if self.options.with_glib:
            self.cpp_info.components["graphene-1.0"].requires = ["glib::gobject-2.0"]

        if self.options.with_glib:
            self.cpp_info.components["graphene-gobject-1.0"].set_property("pkg_config_name","graphene-gobject-1.0")
            self.cpp_info.components["graphene-gobject-1.0"].includedirs = [os.path.join("include", "graphene-1.0")]
            self.cpp_info.components["graphene-gobject-1.0"].requires = ["graphene-1.0", "glib::gobject-2.0"]

    def package_id(self):
        if self.options.with_glib and not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
