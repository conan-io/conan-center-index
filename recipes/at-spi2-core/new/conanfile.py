from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
import os


required_conan_version = ">=1.60.0 <2.0 || >=2.0.5"

class AtSpi2CoreConan(ConanFile):
    name = "at-spi2-core"
    description = "It provides a Service Provider Interface for the Assistive Technologies available on the GNOME platform and a library against which applications can be linked"
    topics = ("atk", "accessibility")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/at-spi2-core/"
    license = "LGPL-2.1-or-later"

    provides = "at-spi2-atk", "atk"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def build_requirements(self):
        self.tool_requires("meson/1.3.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        self.tool_requires("glib/<host_version>")

    def requirements(self):
        self.requires("glib/2.78.3")
        if self.options.with_x11:
            self.requires("xorg/system")
        if self.settings.os == "Linux":
            self.requires("dbus/1.15.8")

    def validate(self):
        if self.options.shared and not  self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if Version(self.version) < "2.49.1":
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("Windows is not supported before version 2.49.1")
        if Version(self.version) < "2.50.0":
            if self.settings.os == "Macos":
                raise ConanInvalidConfiguration("macos is not supported before version 2.50.0")

    def layout(self):
        basic_layout(self, src_folder="src")
        self.cpp.package.resdirs = ["res"]

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        tc = MesonToolchain(self)
        if Version(self.version) >= "2.47.1":
            tc.project_options["introspection"] = "disabled"
            tc.project_options["x11"] = "enabled" if self.options.with_x11 else "disabled"
        else:
            tc.project_options["introspection"] = "no"
            tc.project_options["x11"] = "yes" if self.options.with_x11 else "no"
        if self.settings.os != "Linux":
            tc.project_options["atk_only"] = "true"
            
        tc.project_options["docs"] = "false"
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "bus", "meson.build"),
                                "if x11_dep.found()",
                                "if get_option('x11').enabled()" if Version(self.version) >= "2.47.1"
                                else "if x11_option == 'yes'")
        replace_in_file(self, os.path.join(self.source_folder, 'meson.build'),
            "subdir('tests')",
            "#subdir('tests')")
        replace_in_file(self, os.path.join(self.source_folder, 'meson.build'),
            "libxml_dep = dependency('libxml-2.0', version: libxml_req_version)",
            "#libxml_dep = dependency('libxml-2.0', version: libxml_req_version)")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)


    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.components["atspi"].libs = ['atspi']
            self.cpp_info.components["atspi"].includedirs = ["include/at-spi-2.0"]
            self.cpp_info.components["atspi"].requires = ["dbus::dbus", "glib::glib"]
            self.cpp_info.components["atspi"].set_property("pkg_config_name", "atspi-2")

        self.cpp_info.components["atk"].libs = ["atk-1.0"]
        self.cpp_info.components["atk"].includedirs = ['include/atk-1.0']
        self.cpp_info.components["atk"].requires = ["glib::glib"]
        self.cpp_info.components["atk"].set_property("pkg_config_name", 'atk')

        if self.settings.os == "Linux":
            self.cpp_info.components["atk-bridge"].libs = ['atk-bridge-2.0']
            self.cpp_info.components["atk-bridge"].includedirs = [os.path.join('include', 'at-spi2-atk', '2.0')]
            self.cpp_info.components["atk-bridge"].requires = ["dbus::dbus", "atk", "glib::glib", "atspi"]
            self.cpp_info.components["atk-bridge"].set_property("pkg_config_name", 'atk-bridge-2.0')


def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib in case of cl like compiler"""
    if not conanfile.settings.get_safe("compiler.runtime"):
        return
    from conan.tools.files import rename
    import glob
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
