from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibalsaConan(ConanFile):
    name = "libalsa"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alsa-project/alsa-lib"
    topics = ("conan", "libalsa", "alsa", "sound", "audio", "midi")
    description = "Library of ALSA: The Advanced Linux Sound Architecture, that provides audio " \
                  "and MIDI functionality to the Linux operating system"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_python": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_python": True,
    }
    settings = "os", "compiler", "build_type", "arch"

    exports_sources = "patches/*"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-python={}".format(yes_no(not self.options.disable_python)),
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
        ]
        self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)

            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["asound"]
        self.cpp_info.system_libs = ["dl", "m", "rt", "pthread"]
        self.cpp_info.names["pkg_config"] = "alsa"
        self.cpp_info.names["cmake_find_package"] = "ALSA"
        self.cpp_info.names["cmake_find_package_multi"] = "ALSA"
        self.env_info.ALSA_CONFIG_DIR = os.path.join(self.package_folder, "res", "alsa")
