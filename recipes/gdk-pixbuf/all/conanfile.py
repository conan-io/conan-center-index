from conan import ConanFile
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.gnu import PkgConfigDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
from conan.tools import files, scm, microsoft
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.52.0"


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
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            self.options["glib"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.info.options.shared and not self.dependencies.direct_host["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if self.info.settings.os == "Macos":
            # when running gdk-pixbuf-query-loaders
            # dyld: malformed mach-o: load commands size (97560) > 32768
            raise ConanInvalidConfiguration("This package does not support Macos currently")
        if self.dependencies.direct_host["glib"].options.shared and microsoft.is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Linking shared glib with the MSVC static runtime is not supported"
            )

    @property
    def _requires_compiler_rt(self):
        return self.settings.compiler == "clang" and scm.Version(self.settings.compiler.version) <= "12" and self.settings.build_type == "Debug"

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
        if scm.Version(self.version) < "2.42.0":
            tc.project_options["gir"] = "false"

        if scm.Version(self.version) >= "2.42.8":
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
        self.requires("glib/2.74.0")
        if self.options.with_libpng:
            self.requires("libpng/1.6.38")
        if self.options.with_libtiff:
            self.requires("libtiff/4.4.0")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")

    def build_requirements(self):
        self.tool_requires("meson/0.63.2")
        self.tool_requires("pkgconf/1.9.3")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def export_sources(self):
        files.export_conandata_patches(self)

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        files.apply_conandata_patches(self)

        meson_build = os.path.join(self.source_folder, "meson.build")
        files.replace_in_file(self, meson_build, "subdir('tests')", "#subdir('tests')")
        files.replace_in_file(self, meson_build, "subdir('thumbnailer')", "#subdir('thumbnailer')")
        files.replace_in_file(self, meson_build,
                              "gmodule_dep.get_variable(pkgconfig: 'gmodule_supported')" if scm.Version(self.version) >= "2.42.6"
                              else "gmodule_dep.get_pkgconfig_variable('gmodule_supported')", "'true'")
        # workaround https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/203
        if scm.Version(self.version) >= "2.42.6":
            files.replace_in_file(self, os.path.join(self.source_folder, "build-aux", "post-install.py"),
                                  "close_fds=True", "close_fds=(sys.platform != 'win32')")
        if scm.Version(self.version) >= "2.42.9":
            files.replace_in_file(self, meson_build, "is_msvc_like ? 'png' : 'libpng'", "'libpng'")
            files.replace_in_file(self, meson_build, "is_msvc_like ? 'jpeg' : 'libjpeg'", "'libjpeg'")
            files.replace_in_file(self, meson_build, "is_msvc_like ? 'tiff' : 'libtiff-4'", "'libtiff-4'")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()

        files.copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if microsoft.is_msvc(self) and not self.options.shared:
            files.rename(self, os.path.join(self.package_folder, "lib", "libgdk_pixbuf-2.0.a"), os.path.join(self.package_folder, "lib", "gdk_pixbuf-2.0.lib"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rm(self, "*.pdb", self.package_folder, recursive=True)

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

        gdk_pixbuf_pixdata = os.path.join(self.package_folder, "bin", "gdk-pixbuf-pixdata")
        self.runenv_info.define_path("GDK_PIXBUF_PIXDATA", gdk_pixbuf_pixdata)
        self.env_info.GDK_PIXBUF_PIXDATA = gdk_pixbuf_pixdata # remove in conan v2?

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "gdk-pixbuf-2.0"

    def package_id(self):
        if not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
