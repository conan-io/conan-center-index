from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class AlsaPluginsConan(ConanFile):
    name = "alsa-plugins"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alsa-project/alsa-plugins"
    topics = ("conan", "libalsa", "alsa", "sound", "audio", "midi")
    description = "The Advanced Linux Sound Architecture (ALSA) - plugins"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_pulse": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_pulse": True
    }
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libalsa/1.2.5.1")
        if self.options.with_pulse:
            self.requires("pulseaudio/14.2")
    
    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")
        if not self.options.shared:
            raise ConanInvalidConfiguration("Static build is not supported")
    
    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, cwd=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.env_info.ALSA_CONFIG_DIR.append(os.path.join(self.package_folder, "res", "alsa", "alsa.conf.d"))
        alsa_plugin_dir = os.path.join(self.package_folder, "lib", "alsa-lib")
        if self.options.shared:
            self.output.info("Appending ALSA_PLUGIN_DIR env var : %s" % alsa_plugin_dir)
            self.env_info.ALSA_PLUGIN_DIR.append(alsa_plugin_dir)
