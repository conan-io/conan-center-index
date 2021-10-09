from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


required_conan_version = ">=1.29.1"



class LibnameConan(ConanFile):
    name = "gdk-pixbuf"
    description = "toolkit for image loading and pixel buffer manipulation"
    topics = ("conan", "gdk-pixbuf", "image")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.gnome.org/gdk-pixbuf/"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_libtiff": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", False],
        "with_jasper": [True, False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libpng": True,
        "with_libtiff": True,
        "with_libjpeg": "libjpeg",
        "with_jasper": False,
        "with_introspection": False,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Macos":
            # when running gdk-pixbuf-query-loaders
            # dyld: malformed mach-o: load commands size (97560) > 32768
            raise ConanInvalidConfiguration("This package does not support Macos currently")
    
    def build_requirements(self):
        self.build_requires("meson/0.57.1")
        self.build_requires("pkgconf/1.7.3")
        if self.options.with_introspection:
            self.build_requires("gobject-introspection/1.68.0")
    
    def requirements(self):
        self.requires("glib/2.69.0")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_libtiff:
            self.requires("libtiff/4.2.0")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.6")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9d")
        if self.options.with_jasper:
            self.requires("jasper/2.0.27")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"), "subdir('tests')", "#subdir('tests')")
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"), "subdir('thumbnailer')", "#subdir('thumbnailer')")
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"), "gmodule_dep.get_pkgconfig_variable('gmodule_supported')", "'true'")

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        defs["gir"] = "false"
        defs["docs"] = "false"
        defs["man"] = "false"
        defs["installed_tests"] = "false"
        defs["png"] = "true" if self.options.with_libpng else "false"
        defs["tiff"] = "true" if self.options.with_libtiff else "false"
        defs["jpeg"] = "true" if self.options.with_libjpeg else "false"
        defs["jasper"] = "true" if self.options.with_jasper else "false"
        defs["x11"] = "false"
        defs["builtin_loaders"] = "all"
        defs["gio_sniffing"] = "false"
        defs["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        args=[]
        args.append("--wrap-mode=nofallback")
        meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=".", args=args)
        return meson

    def build(self):
        if self.options.with_libpng:
            shutil.move("libpng.pc", "libpng16.pc")
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append({"LD_LIBRARY_PATH": os.path.join(self.package_folder, "lib")}):
            meson = self._configure_meson()
            meson.install()
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "libgdk_pixbuf-2.0.a"), os.path.join(self.package_folder, "lib", "gdk_pixbuf-2.0.lib"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include/gdk-pixbuf-2.0"]
        self.cpp_info.names["pkg_config"] = "gdk-pixbuf-2.0"
        if not self.options.shared:
            self.cpp_info.defines.append("GDK_PIXBUF_STATIC_COMPILATION")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        self.env_info.GDK_PIXBUF_PIXDATA = os.path.join(self.package_folder, "bin", "gdk-pixbuf-pixdata")
