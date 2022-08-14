from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.options.enable_lib:
            del self.options.fPIC
            del self.options.shared
        elif self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def package_id(self):
        if not self.options.enable_lib:
            del self.info.settings.compiler

    def build_requirements(self):
        self.tool_requires("meson/0.63.1")

    def layout(self):
        basic_layout(self, src_folder="src")

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
        # TODO: fixed in conan 1.51.0?
        tc.project_options["bindir"] = "bin"
        tc.project_options["libdir"] = "lib"
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate(scope="build")

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

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        exesuffix = ".exe" if self.settings.os == "Windows" else ""
        pkg_config = os.path.join(bindir, "pkgconf" + exesuffix).replace("\\", "/")
        self.output.info("Setting PKG_CONFIG env var: {}".format(pkg_config))
        self.buildenv_info.define_path("PKG_CONFIG", pkg_config)
        self.env_info.PKG_CONFIG = pkg_config # remove in conan v2?

        automake_extra_includes = unix_path(self, os.path.join(self.package_folder , "bin", "aclocal").replace("\\", "/"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES env var: {}".format(automake_extra_includes))
        self.buildenv_info.prepend_path("AUTOMAKE_CONAN_INCLUDES", automake_extra_includes)
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(automake_extra_includes) # remove in conan v2?

        # TODO: to remove in conan v2 once pkg_config generator removed
        if self.options.enable_lib:
            self.cpp_info.names["pkg_config"] = "libpkgconf"

def fix_msvc_libname(conanfile):
    """remove lib prefix & change extension to .lib"""
    import glob
    if not is_msvc(conanfile):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.splitext(os.path.basename(filepath))[0]
                if libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
