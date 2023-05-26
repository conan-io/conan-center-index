from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import glob
import os

required_conan_version = ">=1.53.0"


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0-only"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("callback")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("meson/1.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["build-examples"] = "false"
        tc.project_options["build-documentation"] = "false"
        tc.generate()

    def _patch_sources(self):
        if not self.options.shared:
            replace_in_file(
                self, os.path.join(self.source_folder, "sigc++config.h.meson"),
                "define SIGC_DLL 1", "undef SIGC_DLL",
            )

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        for header_file in glob.glob(os.path.join(self.package_folder, "lib", "sigc++-2.0", "include", "*.h")):
            dst = os.path.join(self.package_folder, "include", "sigc++-2.0", os.path.basename(header_file))
            rename(self, header_file, dst)
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "sigc++-2.0"))
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sigc++-2.0")
        self.cpp_info.includedirs.append(os.path.join("include", "sigc++-2.0"))
        self.cpp_info.libs = ["sigc-2.0"]

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib"""
    from conan.tools.files import rename
    from conan.tools.microsoft import is_msvc
    import glob
    import os
    if not is_msvc(conanfile):
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
