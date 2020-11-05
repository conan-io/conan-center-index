import os

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration

class GtkmmConan(ConanFile):
    name = "gtkmm"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    homepage = "https://www.gtk.org"
    description = "The C++ API for GTK."
    settings = {"os": "Linux"}
    options = {"version": [2]}
    default_options = {"version": 2}
    topics = ("gui", "widget", "graphical")

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
              }
    default_options = {"shared": False,
                       "fPIC": True}
    generators = "pkg_config"
    _autoconf = None

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
        if self.settings.compiler == "Visual Studio" and \
           "MT" in str(self.settings.compiler.runtime) and self.options.shared:
            raise ConanInvalidConfiguration("Visual Studio and Runtime MT is not supported for shared library.")
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        self.requires('gtk/system')
        self.requires('libsigcpp/3.0.0')

    def _configure_build(self):
        if self._autoconf:
            return self._autoconf

        self._autoconf = AutoToolsBuildEnvironment(self)
        return self._autoconf

    def build(self):
        tools.replace_in_file(self._source_subfolder + '/configure', "gtk+-2.0 >= 2.24.0", "gtk+-2.0")

        autoconf = self._configure_build()
        autoconf.configure(configure_dir=self._source_subfolder,
                            vars = {
                                'cross_compiling': 'no'
                            }
                          )
        autoconf.make()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        autoconf = self._configure_build()
        autoconf.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = ['include', 'include/gtkmm-2.4', 'include/gdkmm-2.4']
        self.cpp_info.libs = tools.collect_libs(self)
