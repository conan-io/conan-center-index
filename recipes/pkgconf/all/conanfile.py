from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.52.0"


class PkgConfConan(ConanFile):
    name = "pkgconf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.sr.ht/~kaniini/pkgconf"
    topics = ("pkgconf")
    license = "ISC"
    description = "package compiler and linker metadata toolkit"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_lib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_lib": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.options.enable_lib:
            try:
                del self.options.fPIC
            except Exception:
                pass
            del self.options.shared
        elif self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        if not self.options.enable_lib:
            del self.info.settings.compiler

    def build_requirements(self):
        self.tool_requires("meson/0.63.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    @property
    def _sharedstatedir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["tests"] = False
        tc.project_options["sharedstatedir"] = self._sharedstatedir
        if not self.options.enable_lib:
            tc.project_options["default_library"] = "static"
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not self.options.get_safe("shared", False):
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                                  "'-DLIBPKGCONF_EXPORT'",
                                  "'-DPKGCONFIG_IS_STATIC'")
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
            "project('pkgconf', 'c',",
            "project('pkgconf', 'c',\ndefault_options : ['c_std=gnu99'],")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        if self.options.enable_lib:
            fix_apple_shared_install_name(self)
            fix_msvc_libname(self)
        else:
            rmdir(self, os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "include"))

        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        rename(self, os.path.join(self.package_folder, "share", "aclocal"),
                     os.path.join(self.package_folder, "bin", "aclocal"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.options.enable_lib:
            self.cpp_info.set_property("pkg_config_name", "libpkgconf")
            if Version(self.version) >= "1.7.4":
                self.cpp_info.includedirs.append(os.path.join("include", "pkgconf"))
            self.cpp_info.libs = ["pkgconf"]
            if not self.options.shared:
                self.cpp_info.defines = ["PKGCONFIG_IS_STATIC"]
        else:
            self.cpp_info.includedirs = []
            self.cpp_info.libdirs = []

        exesuffix = ".exe" if self.settings.os == "Windows" else ""
        pkg_config = os.path.join(self.package_folder, "bin", f"pkgconf{exesuffix}").replace("\\", "/")
        self.conf_info.define("tools.gnu:pkg_config", pkg_config)
        self.buildenv_info.define_path("PKG_CONFIG", pkg_config)

        # TODO: replace by conan.tools.microsoft.unix_path when stateless
        # (see https://github.com/conan-io/conan/issues/12192)
        automake_extra_includes = tools_legacy.unix_path(os.path.join(self.package_folder , "bin", "aclocal").replace("\\", "/"))
        self.output.info(f"Appending AUTOMAKE_CONAN_INCLUDES env var: {automake_extra_includes}")
        self.buildenv_info.prepend_path("AUTOMAKE_CONAN_INCLUDES", automake_extra_includes)

        # TODO: to remove in conan v2
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
        self.env_info.PKG_CONFIG = pkg_config
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(automake_extra_includes)

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib"""
    import glob
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
