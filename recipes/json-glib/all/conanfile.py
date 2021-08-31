from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment

import os
import glob
import shutil

required_conan_version = ">=1.29"

class JsonGlibConan(ConanFile):
    name = "json-glib"
    description = "JSON-GLib implements a full JSON parser and generator using GLib and GObject, and integrates JSON with GLib data types."
    topics = ("json", "glib")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wiki.gnome.org/Projects/JsonGlib"
    license = "GNU LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_introspection": ['enabled', 'auto', 'disabled'],
        "gtk_doc": ['enabled', 'auto', 'disabled'],
        "man": [True, False],
        "tests": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_introspection": 'auto',
        "gtk_doc": 'auto',
        "man": False,
        "tests": False,
    }
    generators = "pkg_config"
    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("glib/2.68.0")

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        # `tests' option was added in 1.5
        if tools.Version(self.version) < '1.5':
            del self.options.tests
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("meson/0.56.2")
        if self.settings.os == 'Windows':
            self.build_requires('pkgconf/1.7.4')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.rename("%s-%s" % (self.name, self.version), self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        meson = Meson(self)
        if self._is_msvc:
            if tools.Version(self.settings.compiler.version) < "14":
                meson.options["c_args"] = " -Dsnprintf=_snprintf"
                meson.options["cpp_args"] = " -Dsnprintf=_snprintf"
        if self.settings.get_safe("compiler.runtime"):
            meson.options["b_vscrt"] = str(self.settings.compiler.runtime).lower()
        meson.options["with_introspection"] = self.options.with_introspection
        meson.options["gtk_doc"] = self.options.gtk_doc
        meson.options["man"] = self.options.man
        if tools.Version(self.version) >= '1.5':
            meson.options["tests"] = self.options.tests
        meson.configure(build_folder=self._build_subfolder,
                        source_folder=self._source_subfolder,
                        args=['--wrap-mode=nofallback'])
        self._meson = meson
        return self._meson

    def build(self):
        env_vars = VisualStudioBuildEnvironment(self).vars
        env_vars['PKG_CONFIG_PATH'] = self.build_folder
        self.output.info('Setting PKG_CONFIG_PATH: ' + env_vars['PKG_CONFIG_PATH'])
        with tools.environment_append(env_vars) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.build()

    def _fix_library_names(self, path):
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    shutil.move(filename_old, filename_new)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.install()
        
        self._fix_library_names(os.path.join(self.package_folder, "lib"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")

    def package_info(self):
        include_dir_1 = os.sep.join(['include', 'json-glib-1.0'])
        self.cpp_info.includedirs = [ include_dir_1 ]

        self.cpp_info.libs = tools.collect_libs(self)
