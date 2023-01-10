from conan import ConanFile
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.gnu import PkgConfigDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rename,
    replace_in_file,
    rm,
    rmdir
)
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.53.0"


class GdkPixbufConan(ConanFile):
    name = "gdk-pixbuf"
    description = "toolkit for image loading and pixel buffer manipulation"
    topics = ("gdk-pixbuf", "image")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.gnome.org/gdk-pixbuf/"
    license = "LGPL-2.1-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_libtiff": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", False],
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

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options["glib"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.info.options.shared and not self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if self.info.settings.os == "Macos":
            # when running gdk-pixbuf-query-loaders
            # dyld: malformed mach-o: load commands size (97560) > 32768
            raise ConanInvalidConfiguration("This package does not support Macos currently")
        if self.dependencies["glib"].options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Linking shared glib with the MSVC static runtime is not supported"
            )

    @property
    def _requires_compiler_rt(self):
        return self.settings.compiler == "clang" and Version(self.settings.compiler.version) <= "12" and self.settings.build_type == "Debug"

    def generate(self):
        def is_enabled(value):
            return "enabled" if value else "disabled"

        def is_true(value):
            return "true" if value else "false"

        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "builtin_loaders": "all",
            "gio_sniffing": "false",
            "introspection": is_enabled(self.options.with_introspection),
            "docs": "false",
            "man": "false",
            "installed_tests": "false"
        })
        if Version(self.version) < "2.42.0":
            tc.project_options["gir"] = "false"

        if Version(self.version) >= "2.42.8":
            tc.project_options.update({
                "png": is_enabled(self.options.with_libpng),
                "tiff": is_enabled(self.options.with_libtiff),
                "jpeg": is_enabled(self.options.with_libjpeg)
            })
        else:
            tc.project_options.update({
                "png": is_true(self.options.with_libpng),
                "tiff": is_true(self.options.with_libtiff),
                "jpeg": is_true(self.options.with_libjpeg)
            })

        # Workaround for https://bugs.llvm.org/show_bug.cgi?id=16404
        # Only really for the purposes of building on CCI - end users can
        # workaround this by appropriately setting global linker flags in their profile
        if self._requires_compiler_rt:
            tc.c_link_args.append("-rtlib=compiler-rt")
        tc.generate()

        venv = VirtualBuildEnv(self)
        venv.generate()

    def requirements(self):
        self.requires("glib/2.75.0")
        if self.options.with_libpng:
            self.requires("libpng/1.6.39")
        if self.options.with_libtiff:
            self.requires("libtiff/4.4.0")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")

    def build_requirements(self):
        self.tool_requires("meson/0.64.1")
        self.tool_requires("pkgconf/1.9.3")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

        meson_build = os.path.join(self.source_folder, "meson.build")
        replace_in_file(self, meson_build, "subdir('tests')", "#subdir('tests')")
        replace_in_file(self, meson_build, "subdir('thumbnailer')", "#subdir('thumbnailer')")
        replace_in_file(self, meson_build,
                              "gmodule_dep.get_variable(pkgconfig: 'gmodule_supported')" if Version(self.version) >= "2.42.6"
                              else "gmodule_dep.get_pkgconfig_variable('gmodule_supported')", "'true'")
        # workaround https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/203
        if Version(self.version) >= "2.42.6":
            replace_in_file(self, os.path.join(self.source_folder, "build-aux", "post-install.py"),
                                  "close_fds=True", "close_fds=(sys.platform != 'win32')")
        if Version(self.version) >= "2.42.9":
            replace_in_file(self, meson_build, "is_msvc_like ? 'png' : 'libpng'", "'libpng'")
            replace_in_file(self, meson_build, "is_msvc_like ? 'jpeg' : 'libjpeg'", "'libjpeg'")
            replace_in_file(self, meson_build, "is_msvc_like ? 'tiff' : 'libtiff-4'", "'libtiff-4'")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()

        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if is_msvc(self) and not self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "libgdk_pixbuf-2.0.a"), os.path.join(self.package_folder, "lib", "gdk_pixbuf-2.0.lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)



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

        pkgconfig_variables = {
            "bindir": "${prefix}/bin",
            "gdk_pixbuf_binary_version": "2.10.0",
            "gdk_pixbuf_binarydir": "${libdir1}/gdk-pixbuf-2.0/2.10",
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

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "gdk-pixbuf-2.0"

    def package_id(self):
        if not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
