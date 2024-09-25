from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import can_run, stdcpp_library
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.scm import Version

import os

required_conan_version = ">=1.60.0 <2.0 || >=2.0.6"


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    description = "HarfBuzz is an OpenType text shaping engine."
    topics = ("opentype", "text", "engine")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://harfbuzz.github.io/"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_icu": [True, False],
        "with_glib": [True, False],
        "with_gdi": [True, False],
        "with_uniscribe": [True, False],
        "with_directwrite": [True, False],
        "with_subset": [True, False],
        "with_coretext": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
        "with_icu": False,
        "with_glib": True,
        "with_gdi": True,
        "with_uniscribe": True,
        "with_directwrite": False,
        "with_subset": False,
        "with_coretext": True,
    }

    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_gdi
            del self.options.with_uniscribe
            del self.options.with_directwrite
        if not is_apple_os(self):
            del self.options.with_coretext

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.shared and self.options.with_glib:
            wildcard = "" if Version(conan_version) < "2.0.0" else "/*"
            self.options[f"glib{wildcard}"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_icu:
            self.requires("icu/74.1")
        if self.options.with_glib:
            self.requires("glib/2.78.3")

    def validate(self):
        if self.options.shared and self.options.with_glib and not self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("New versions of harfbuzz require at least gcc 7")

        if self.options.with_glib and self.dependencies["glib"].options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Linking shared glib with the MSVC static runtime is not supported"
            )

    def build_requirements(self):
        self.tool_requires("meson/1.4.0")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self.options.with_glib:
            self.tool_requires("glib/<host_version>")
        if self.settings.os == "Macos":
            # Ensure that the gettext we use at build time is compatible
            # with the libiconv that is transitively exposed by glib
            self.tool_requires("gettext/0.21")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def is_enabled(value):
            return "enabled" if value else "disabled"

        def meson_backend_and_flags():
            def is_vs_2017():
                version = Version(self.settings.compiler.version)
                return version == "15" or version == "191"

            if is_msvc(self) and is_vs_2017() and self.settings.build_type == "Debug":
                # Mitigate https://learn.microsoft.com/en-us/cpp/build/reference/zf?view=msvc-170
                return "vs", ["/bigobj"]
            return "ninja", []

        VirtualBuildEnv(self).generate()

        # Avoid conflicts with libiconv
        # see: https://github.com/conan-io/conan-center-index/pull/17046#issuecomment-1554629094
        if self._settings_build.os == "Macos":
            env = Environment()
            env.define_path("DYLD_FALLBACK_LIBRARY_PATH", "$DYLD_LIBRARY_PATH")
            env.define_path("DYLD_LIBRARY_PATH", "")
            env.vars(self, scope="build").save_script("conanbuild_macos_runtimepath")

        PkgConfigDeps(self).generate()

        backend, cxxflags = meson_backend_and_flags()
        tc = MesonToolchain(self, backend=backend)
        tc.project_options["auto_features"] = "disabled"
        tc.project_options.update({
            "glib": is_enabled(self.options.with_glib),
            "icu": is_enabled(self.options.with_icu),
            "freetype": is_enabled(self.options.with_freetype),
            "gdi": is_enabled(self.options.get_safe("with_gdi")),
            "coretext": is_enabled(self.options.get_safe("with_coretext")),
            "directwrite": is_enabled(self.options.get_safe("with_directwrite")),
            "gobject": is_enabled(can_run(self) and self.options.with_glib),
            "introspection": is_enabled(False),
            "tests": "disabled",
            "docs": "disabled",
            "benchmark": "disabled",
            "icu_builtin": "false"
        })
        tc.cpp_args += cxxflags
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('util')", "")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "harfbuzz")
        self.cpp_info.set_property("cmake_target_name", "harfbuzz::harfbuzz")
        self.cpp_info.set_property("pkg_config_name", "harfbuzz")
        if self.options.with_icu:
            self.cpp_info.libs.append("harfbuzz-icu")
        if self.options.with_subset:
            self.cpp_info.libs.append("harfbuzz-subset")
        self.cpp_info.libs.append("harfbuzz")
        self.cpp_info.includedirs.append(os.path.join("include", "harfbuzz"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs.append("user32")
            if self.options.with_gdi or self.options.with_uniscribe:
                self.cpp_info.system_libs.append("gdi32")
            if self.options.with_uniscribe or self.options.with_directwrite:
                self.cpp_info.system_libs.append("rpcrt4")
            if self.options.with_uniscribe:
                self.cpp_info.system_libs.append("usp10")
            if self.options.with_directwrite:
                self.cpp_info.system_libs.append("dwrite")
        if is_apple_os(self) and self.options.get_safe("with_coretext", False):
            if self.settings.os == "Macos":
                self.cpp_info.frameworks.append("ApplicationServices")
            else:
                self.cpp_info.frameworks.extend(["CoreFoundation", "CoreGraphics", "CoreText"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)


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
