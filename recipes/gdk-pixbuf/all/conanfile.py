from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os
import shutil

required_conan_version = ">=1.36.0"


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

    generators = "pkg_config"
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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

    def requirements(self):
        if self.settings.compiler == "clang":
            # FIXME: cannot bump glib due to "undefined reference to `__muloti4'"
            # see https://github.com/conan-io/conan-center-index/pull/10154#issuecomment-1094224794
            self.requires("glib/2.70.4")
        else:
            self.requires("glib/2.73.0")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_libtiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9d")

    def validate(self):
        if self.options.shared and not self.options["glib"].shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if self.settings.os == "Macos":
            # when running gdk-pixbuf-query-loaders
            # dyld: malformed mach-o: load commands size (97560) > 32768
            raise ConanInvalidConfiguration("This package does not support Macos currently")

    def build_requirements(self):
        self.build_requires("meson/0.61.2")
        self.build_requires("pkgconf/1.7.4")
        if self.options.with_introspection:
            self.build_requires("gobject-introspection/1.70.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        meson_build = os.path.join(self._source_subfolder, "meson.build")
        tools.replace_in_file(meson_build, "subdir('tests')", "#subdir('tests')")
        tools.replace_in_file(meson_build, "subdir('thumbnailer')", "#subdir('thumbnailer')")
        tools.replace_in_file(meson_build,
                              "gmodule_dep.get_variable(pkgconfig: 'gmodule_supported')" if tools.Version(self.version) >= "2.42.6"
                              else "gmodule_dep.get_pkgconfig_variable('gmodule_supported')", "'true'")
        # workaround https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/203
        if tools.Version(self.version) >= "2.42.6":
            tools.replace_in_file(os.path.join(self._source_subfolder, "build-aux", "post-install.py"),
                                  "close_fds=True", "close_fds=(sys.platform != 'win32')")

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        if tools.Version(self.version) >= "2.42.0":
            defs["introspection"] = "false"
        else:
            defs["gir"] = "false"
        defs["docs"] = "false"
        defs["man"] = "false"
        defs["installed_tests"] = "false"
        if tools.Version(self.version) >= "2.42.8":
            defs["png"] = "enabled" if self.options.with_libpng else "disabled"
            defs["tiff"] = "enabled" if self.options.with_libtiff else "disabled"
            defs["jpeg"] = "enabled" if self.options.with_libjpeg else "disabled"
        else:
            defs["png"] = "true" if self.options.with_libpng else "false"
            defs["tiff"] = "true" if self.options.with_libtiff else "false"
            defs["jpeg"] = "true" if self.options.with_libjpeg else "false"

        defs["builtin_loaders"] = "all"
        defs["gio_sniffing"] = "false"
        defs["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        args=[]
        args.append("--wrap-mode=nofallback")
        meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=".", args=args)
        return meson

    def build(self):
        self._patch_sources()
        if self.options.with_libpng:
            shutil.copy("libpng.pc", "libpng16.pc")
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append({"LD_LIBRARY_PATH": os.path.join(self.package_folder, "lib")}):
            meson = self._configure_meson()
            meson.install()
        if str(self.settings.compiler) in ["Visual Studio", "msvc"] and not self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "libgdk_pixbuf-2.0.a"), os.path.join(self.package_folder, "lib", "gdk_pixbuf-2.0.lib"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gdk-pixbuf-2.0")
        self.cpp_info.libs = ["gdk_pixbuf-2.0"]
        self.cpp_info.includedirs = [os.path.join("include", "gdk-pixbuf-2.0")]
        if not self.options.shared:
            self.cpp_info.defines.append("GDK_PIXBUF_STATIC_COMPILATION")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

        gdk_pixbuf_pixdata = os.path.join(self.package_folder, "bin", "gdk-pixbuf-pixdata")
        self.runenv_info.define_path("GDK_PIXBUF_PIXDATA", gdk_pixbuf_pixdata)
        self.env_info.GDK_PIXBUF_PIXDATA = gdk_pixbuf_pixdata # remove in conan v2?

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "gdk-pixbuf-2.0"

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
