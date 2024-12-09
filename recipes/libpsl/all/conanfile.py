import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class LibPslConan(ConanFile):
    name = "libpsl"
    description = "C library for the Public Suffix List"
    homepage = "https://github.com/rockdaboot/libpsl"
    topics = ("psl", "suffix", "TLD", "gTLD", ".com", ".net")
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_idna": [False, "icu", "libidn", "libidn2"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_idna": "icu",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_idna == "icu":
            self.requires("icu/74.1")
        elif self.options.with_idna == "libidn":
            self.requires("libidn/1.36")
        elif self.options.with_idna == "libidn2":
            self.requires("libidn2/2.3.0")
        if self.options.with_idna in ("libidn", "libidn2"):
            self.requires("libunistring/1.1")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2.0 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _idna_option(self):
        return {
            "False": "no",
            "icu": "libicu",
        }.get(str(self.options.with_idna), str(self.options.with_idna))

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["runtime"] = self._idna_option
        if Version(self.version) >= "0.21.5":
            tc.project_options["builtin"] = "true" if self.options.with_idna else "false"
            tc.project_options["tests"] = "false"  # disable tests and fuzzes
        else:
            tc.project_options["builtin"] = self._idna_option
        if not self.options.shared:
            tc.preprocessor_definitions["PSL_STATIC"] = "1"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libpsl")
        self.cpp_info.libs = ["psl"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        if not self.options.shared:
            self.cpp_info.defines = ["PSL_STATIC"]

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
