from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import shutil
import glob


class GLibConan(ConanFile):
    name = "glib"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    topics = ("conan", "glib", "gobject", "gio", "gmodule")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/glib"
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_pcre": [True, False],
               "with_elf": [True, False],
               "with_selinux": [True, False],
               "with_mount": [True, False]}
    default_options = {"shared": True,
                       "fPIC": True,
                       "with_pcre": True,
                       "with_elf": True,
                       "with_mount": True,
                       "with_selinux": True}
    requires = "zlib/1.2.11", "libffi/3.2.1"
    short_paths = True
    generators = "pkg_config"

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if (self.settings.os == "Windows" and not self.options.shared) or\
           "MT" in self.settings.get_safe("compiler.runtime", default=""):
            raise ConanInvalidConfiguration("glib can not be built as static library on Windows. "\
                                           "see https://gitlab.gnome.org/GNOME/glib/-/issues/692")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_mount
            del self.options.with_selinux

    def build_requirements(self):
        self.build_requires("meson/0.55.0")
        self.build_requires("pkgconf/1.7.3")

    def requirements(self):
        if self.options.with_pcre:
            self.requires("pcre/8.41")
        if self.options.with_elf:
            self.requires("libelf/0.8.13")
        if self.settings.os == "Linux":
            if self.options.with_mount:
                self.requires("libmount/2.33.1")
            if self.options.with_selinux:
                self.requires("libselinux/2.9")
        else:
            # for Linux, gettext is provided by libc
            self.requires("libgettext/0.20.1")

        if tools.is_apple_os(self.settings.os):
            self.requires("libiconv/1.16")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"), \
            "build_tests = not meson.is_cross_build() or (meson.is_cross_build() and meson.has_exe_wrapper())", \
            "build_tests = false")
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"), \
            "subdir('fuzzing')", \
            "#subdir('fuzzing')") # https://gitlab.gnome.org/GNOME/glib/-/issues/2152

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        if tools.is_apple_os(self.settings.os):
            self._meson.options["iconv"] = "external"  # https://gitlab.gnome.org/GNOME/glib/issues/1557
        if self.settings.os == "Linux":
            self._meson.options["selinux"] = "enabled" if self.options.with_selinux else "disabled"
            self._meson.options["libmount"] = "enabled" if self.options.with_mount else "disabled"
        self._meson.options["internal_pcre"] = not self.options.with_pcre

        self._meson.configure(source_folder=self._source_subfolder, args=["--wrap-mode=nofallback"],
                              build_folder=self._build_subfolder)
        return self._meson

    def build(self):
        for filename in [os.path.join(self._source_subfolder, "meson.build"),
                         os.path.join(self._source_subfolder, "glib", "meson.build"),
                         os.path.join(self._source_subfolder, "gobject", "meson.build"),
                         os.path.join(self._source_subfolder, "gio", "meson.build")]:
            tools.replace_in_file(filename, "subdir('tests')", "#subdir('tests')")
        # allow to find gettext
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                              "libintl = cc.find_library('intl', required : false)",
                              "libintl = cc.find_library('gnuintl', required : false)")
        if self.settings.os != "Linux":
            tools.replace_in_file(os.path.join(self._source_subfolder, 'meson.build'),
                                "if cc.has_function('ngettext')",
                                "if false #cc.has_function('ngettext')")

        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.build()

    def _fix_library_names(self):
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    shutil.move(filename_old, filename_new)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.install()
            self._fix_library_names()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share", "bash-completion"))
        tools.rmdir(os.path.join(self.package_folder, "share", "gettext"))
        tools.rmdir(os.path.join(self.package_folder, "share", "locale"))
        for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb_file)

        shutil.move(os.path.join(self.package_folder, "share"),
                    os.path.join(self.package_folder, "bin", "share"))

    def package_info(self):

        self.cpp_info.components["libglib"].libs = ["glib-2.0"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libglib"].system_libs.append("pthread")
        if self.settings.os == "Windows":
            self.cpp_info.components["libglib"].system_libs.extend(["ws2_32", "ole32", "shell32", "user32", "advapi32"])
        if self.settings.os == "Macos":
            self.cpp_info.components["libglib"].system_libs.append("iconv")
            self.cpp_info.components["libglib"].system_libs.append("resolv")
            self.cpp_info.components["libglib"].frameworks.extend(['Foundation', 'CoreServices', 'CoreFoundation'])
        self.cpp_info.components["libglib"].includedirs.append(os.path.join('include', 'glib-2.0'))
        self.cpp_info.components["libglib"].includedirs.append(os.path.join('lib', 'glib-2.0', 'include'))
        if self.options.with_pcre:
            self.cpp_info.components["libglib"].requires.append("pcre::pcre")
        if self.settings.os != "Linux":
            self.cpp_info.components["libglib"].requires.append("libgettext::libgettext")
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["libglib"].requires.append("libiconv::libiconv")
        self.cpp_info.components["libglib"].names["cmake_find_package"] = "glib-2.0"
        self.cpp_info.components["libglib"].names["cmake_find_package_multi"] = "glib-2.0"
        self.cpp_info.components["libglib"].names["pkg_config"] = "glib-2.0"

        self.cpp_info.components["gmodule"].libs = ["gmodule-2.0"]
        if self.settings.os == "Linux":
            self.cpp_info.components["gmodule"].system_libs.append("pthread")
            self.cpp_info.components["gmodule"].system_libs.append("dl")
        self.cpp_info.components["gmodule"].requires.append("libglib")
        self.cpp_info.components["gmodule"].names["cmake_find_package"] = "gmodule-2.0"
        self.cpp_info.components["gmodule"].names["cmake_find_package_multi"] = "gmodule-2.0"
        self.cpp_info.components["gmodule"].names["pkg_config"] = "gmodule-2.0"

        self.cpp_info.components["gobject"].libs = ["gobject-2.0"]
        self.cpp_info.components["gobject"].requires.append("libglib")
        self.cpp_info.components["gobject"].requires.append("libffi::libffi")
        self.cpp_info.components["gobject"].names["cmake_find_package"] = "gobject-2.0"
        self.cpp_info.components["gobject"].names["cmake_find_package_multi"] = "gobject-2.0"
        self.cpp_info.components["gobject"].names["pkg_config"] = "gobject-2.0"

        self.cpp_info.components["gthread"].libs = ["gthread-2.0"]
        if self.settings.os == "Linux":
            self.cpp_info.components["gthread"].system_libs.append("pthread")
        self.cpp_info.components["gthread"].requires.append("libglib")
        self.cpp_info.components["gthread"].names["cmake_find_package"] = "gthread-2.0"
        self.cpp_info.components["gthread"].names["cmake_find_package_multi"] = "gthread-2.0"
        self.cpp_info.components["gthread"].names["pkg_config"] = "gthread-2.0"

        self.cpp_info.components["gio"].libs = ["gio-2.0"]
        if self.settings.os == "Linux":
            self.cpp_info.components["gio"].system_libs.append("resolv")
            self.cpp_info.components["gio"].system_libs.append("dl")
        self.cpp_info.components["gio"].requires.extend(["libglib", "gobject", "gmodule", "zlib::zlib"])
        if self.settings.os == "Linux":
            if self.options.with_mount:
                self.cpp_info.components["gio"].requires.append("libmount::libmount")
            if self.options.with_selinux:
                self.cpp_info.components["gio"].requires.append("libselinux::libselinux")
        self.cpp_info.components["gio"].names["cmake_find_package"] = "gio-2.0"
        self.cpp_info.components["gio"].names["cmake_find_package_multi"] = "gio-2.0"
        self.cpp_info.components["gio"].names["pkg_config"] = "gio-2.0"

        self.cpp_info.components["gresource"].libs = [] # this is actualy an executable
        self.cpp_info.components["gresource"].requires.append("libelf::libelf") # this is actualy an executable

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        aclocal_path = os.path.join(bin_path, "share", "aclocal")
        self.output.info("Appending ACLOCAL_PATH environment variable: {}".format(aclocal_path))
        self.env_info.ACLOCAL_PATH.append(aclocal_path)
