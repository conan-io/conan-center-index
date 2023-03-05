import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GrapheneConan(ConanFile):
    name = "graphene"
    description = "A thin layer of graphic data types."
    topics = ("graphic", "canvas", "types")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ebassi.github.io/graphene/"
    license = "MIT"
    package_type = "library"
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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.shared and self.options.with_glib:
            self.options["glib"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.75.2")

    def validate(self):
        if self.settings.compiler == "gcc":
            if Version(self.settings.compiler.version) < "5.0":
                raise ConanInvalidConfiguration("graphene does not support GCC before 5.0")

        if self.options.with_glib:
            glib_is_shared = self.dependencies["glib"].options.shared
            if self.options.shared and not glib_is_shared:
                raise ConanInvalidConfiguration(
                    "Linking a shared library against static glib can cause unexpected behaviour."
                )
            if glib_is_shared and is_msvc_static_runtime(self):
                raise ConanInvalidConfiguration(
                    "Linking shared glib with the MSVC static runtime is not supported"
                )

    def build_requirements(self):
        self.tool_requires("meson/1.0.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        meson = MesonToolchain(self)
        meson.project_options.update({
            "tests": "false",
            "installed_tests": "false",
            "gtk_doc": "false",
        })
        meson.project_options["gobject_types"] = "true" if self.options.with_glib else "false"
        if Version(self.version) < "1.10.4":
            meson.project_options["introspection"] = "false"
        else:
            meson.project_options["introspection"] = "disabled"
        meson.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

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
