import os

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.56.0 <2 || >=2.0.8"


class GdkPixbufConan(ConanFile):
    name = "gdk-pixbuf"
    description = "toolkit for image loading and pixel buffer manipulation"
    topics = "image"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.gnome.org/gdk-pixbuf/"
    license = "LGPL-2.1-or-later"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_libtiff": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg", False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libpng": True,
        "with_libtiff": True,
        "with_libjpeg": "libjpeg",
        "with_introspection": False,
    }
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            wildcard = "" if Version(conan_version) < "2.0.0" else "/*"
            self.options[f"glib{wildcard}"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.1", transitive_headers=True, transitive_libs=True)
        if self.options.with_libpng:
            self.requires("libpng/1.6.40")
        if self.options.with_libtiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.1")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.3")

    def validate(self):
        if self.options.shared and not self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if self.dependencies["glib"].options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Linking shared glib with the MSVC static runtime is not supported"
            )

    def build_requirements(self):
        self.tool_requires("meson/1.2.3")
        # FIXME: unify libgettext and gettext??
        # INFO: gettext provides msgfmt, which is required to build the .mo files
        self.tool_requires("gettext/0.21")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        self.tool_requires("glib/<host_version>")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _requires_compiler_rt(self):
        return self.settings.compiler == "clang" and Version(self.settings.compiler.version) <= "12" and self.settings.build_type == "Debug"

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if can_run(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        deps = PkgConfigDeps(self)
        deps.generate()
        tc = MesonToolchain(self)
        enabled_disabled = lambda v: "enabled" if v else "disabled"
        true_false = lambda v: "true" if v else "false"
        tc.project_options.update({
            "builtin_loaders": "all",
            "gio_sniffing": "false",
            "introspection": enabled_disabled(self.options.with_introspection),
            "docs": "false",
            "man": "false",
            "installed_tests": "false"
        })
        if Version(self.version) < "2.42.0":
            tc.project_options["gir"] = "false"

        if Version(self.version) >= "2.42.8":
            tc.project_options.update({
                "png": enabled_disabled(self.options.with_libpng),
                "tiff": enabled_disabled(self.options.with_libtiff),
                "jpeg": enabled_disabled(self.options.with_libjpeg)
            })
        else:
            tc.project_options.update({
                "png": true_false(self.options.with_libpng),
                "tiff": true_false(self.options.with_libtiff),
                "jpeg": true_false(self.options.with_libjpeg)
            })
        # Workaround for https://bugs.llvm.org/show_bug.cgi?id=16404
        # Only really for the purposes of building on CCI - end users can
        # workaround this by appropriately setting global linker flags in their profile
        if self._requires_compiler_rt:
            tc.c_link_args.append("-rtlib=compiler-rt")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        meson_build = os.path.join(self.source_folder, "meson.build")
        gdk_meson_build = os.path.join(self.source_folder, "gdk-pixbuf", "meson.build")

        replace_in_file(self, meson_build, "subdir('tests')", "#subdir('tests')")
        replace_in_file(self, meson_build, "subdir('thumbnailer')", "#subdir('thumbnailer')")
        replace_in_file(self, meson_build, "gmodule_dep.get_variable(pkgconfig: 'gmodule_supported')", "'true'")
        # workaround https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/203
        replace_in_file(self, os.path.join(self.source_folder, "build-aux", "post-install.py"),
                        "close_fds=True", "close_fds=(sys.platform != 'win32')")
        if Version(self.version) >= "2.42.9":
            replace_in_file(self, meson_build, "is_msvc_like = ", "is_msvc_like = false #")
        # Fix libtiff and libpng not being linked against when building statically
        # Reported upstream: https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/merge_requests/159
        replace_in_file(self, gdk_meson_build,
                        "dependencies: gdk_pixbuf_deps + [ gdkpixbuf_dep ],",
                        "dependencies: loaders_deps + gdk_pixbuf_deps + [ gdkpixbuf_dep ],")
        # Forcing Conan libgettext instead of system one (if OS != Linux)
        if self.settings.os != "Linux":
            # FIXME: unify libgettext and gettext ??
            replace_in_file(self, meson_build,
                            "intl_dep = cc.find_library('intl', required: false)",
                            "intl_dep = dependency('libgettext', version: '>=0.21', required: false, method: 'pkg-config')")
        if self.settings.os == "Macos" and self.options.shared:
            # Workaround to avoid generating gdk-pixbuf/loaders.cache fails
            # Error output:
            #   [167/167] Generating gdk-pixbuf/loaders.cache with a custom command (wrapped by meson to capture output)
            #   FAILED: gdk-pixbuf/loaders.cache
            #   meson.py --internal exe --capture gdk-pixbuf/loaders.cache -- xxxx/gdk-pixbuf/gdk-pixbuf-query-loaders
            #   --- stderr ---
            #   dyld[25158]: Library not loaded: /lib/libgnuintl.8.dylib
            #   Reason: tried: '/lib/libgnuintl.8.dylib' (no such file), '/System/Volumes/Preboot/Cryptexes/OS/lib/libgnuintl.8.dylib' (no such file)
            #
            # Obviously, the libgnuintl.8.dylib is in the VirtualRunEnv, but the current env is not passed to
            # the meson custom_target function as it's wrappering the execution
            # custom_target admits also an "env" parameter, but it's not working as expected
            replace_in_file(self, gdk_meson_build, "build_by_default: true", "build_by_default: false")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gdk-pixbuf-2.0")
        self.cpp_info.libs = ["gdk_pixbuf-2.0"]
        self.cpp_info.includedirs = [os.path.join("include", "gdk-pixbuf-2.0")]
        if not self.options.shared:
            self.cpp_info.defines.append("GDK_PIXBUF_STATIC_COMPILATION")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        if self._requires_compiler_rt:
            ldflags = ["-rtlib=compiler-rt"]
            self.cpp_info.exelinkflags = ldflags
            self.cpp_info.sharedlinkflags = ldflags

        # Breaking change since Conan >= 2.0.8
        # Related to https://github.com/conan-io/conan/pull/14233
        libdir_variable = "libdir1" if Version(conan_version) < "2.0" else "libdir"
        pkgconfig_variables = {
            "bindir": "${prefix}/bin",
            "gdk_pixbuf_binary_version": "2.10.0",
            "gdk_pixbuf_binarydir": "${%s}/gdk-pixbuf-2.0/2.10" % libdir_variable,
            "gdk_pixbuf_moduledir": "${gdk_pixbuf_binarydir}/loaders",
            "gdk_pixbuf_cache_file": "${gdk_pixbuf_binarydir}/loaders.cache",
            "gdk_pixbuf_csource": "${bindir}/gdk-pixbuf-csource",
            "gdk_pixbuf_pixdata": "${bindir}/gdk-pixbuf-pixdata",
            "gdk_pixbuf_query_loaders": "${bindir}/gdk-pixbuf-query-loaders"
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()))

        gdk_pixbuf_pixdata = os.path.join(self.package_folder, "bin", "gdk-pixbuf-pixdata")
        self.runenv_info.define_path("GDK_PIXBUF_PIXDATA", gdk_pixbuf_pixdata)
        self.env_info.GDK_PIXBUF_PIXDATA = gdk_pixbuf_pixdata # remove in conan v2?


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
