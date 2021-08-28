from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class LibalsaConan(ConanFile):
    name = "libalsa"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alsa-project/alsa-lib"
    topics = ("alsa", "libalsa", "alsa-plugins", "sound", "audio", "midi")
    description = "Library of ALSA: The Advanced Linux Sound Architecture, that provides audio " \
                  "and MIDI functionality to the Linux operating system"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_python": [True, False],
        "with_plugins": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_python": True,
        "with_plugins": False
    }
    settings = "os", "compiler", "build_type", "arch"

    exports_sources = ["patches/*"]
    generators = "pkg_config"
    _autotools = None
    _plugins_autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _plugins_source_subfolder(self):
        return os.path.join(self._source_subfolder, "plugins")
    
    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_plugins:
            self.requires("pulseaudio/14.2")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")
    
    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)
        tools.get(**self.conan_data["plugins"][self.version], destination=self._plugins_source_subfolder, strip_root=True)

    def _configure_autotools(self, is_plugin):
        autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format("yes" if is_plugin else yes_no(self.options.shared)),
            "--enable-static={}".format("no" if is_plugin else yes_no(not self.options.shared)),
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
        ]
        if not is_plugin:
            args.append("--enable-python={}".format(yes_no(not self.options.disable_python)))
        
        source_dir = self._plugins_source_subfolder if is_plugin else self._source_subfolder
        autotools.configure(args=args, configure_dir=source_dir)
        return autotools
    
    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch) 
        
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, cwd=self._source_subfolder)
        self._autotools = self._configure_autotools(is_plugin=False)
        self._autotools.make()
        
        if self.options.with_plugins:
            # we have to package libalsa so that it can be used to build the plugins
            self._autotools.install()
            shutil.copyfile(os.path.join("utils", "alsa.pc"), "alsa.pc")

            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, cwd=self._plugins_source_subfolder)
            self._plugins_autotools = self._configure_autotools(is_plugin=True)
            self._plugins_autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if not self.options.with_plugins:
            self._autotools.install()

        if self.options.with_plugins:
            self.copy("COPYING", dst=os.path.join("licenses", "plugins"), src=os.path.join(self._source_subfolder, "plugins"))
            self._plugins_autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["asound"]
        self.cpp_info.system_libs = ["dl", "m", "rt", "pthread"]
        self.cpp_info.names["pkg_config"] = "alsa"
        self.cpp_info.names["cmake_find_package"] = "ALSA"
        self.cpp_info.names["cmake_find_package_multi"] = "ALSA"
        self.env_info.ALSA_CONFIG_DIR = os.path.join(self.package_folder, "res", "alsa")
        if self.options.with_plugins:
            alsa_plugin_dir = os.path.join(self.package_folder, "lib", "alsa-lib")
            self.output.info("Appending ALSA_PLUGIN_DIR env var : %s" % alsa_plugin_dir)
            self.env_info.ALSA_PLUGIN_DIR = alsa_plugin_dir
