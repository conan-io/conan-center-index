from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class LibalsaConan(ConanFile):
    name = "libalsa"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alsa-project/alsa-lib"
    topics = ("libalsa", "alsa", "sound", "audio", "midi")
    description = "Library of ALSA: The Advanced Linux Sound Architecture, that provides audio " \
                  "and MIDI functionality to the Linux operating system"

    settings = "os", "compiler", "build_type", "arch"
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

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

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
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ALSA")
        self.cpp_info.set_property("cmake_target_name", "ALSA::ALSA")
        self.cpp_info.set_property("pkg_config_name", "alsa")
        self.cpp_info.libs = ["asound"]
        self.cpp_info.system_libs = ["dl", "m", "rt", "pthread"]
        alsa_config_dir = os.path.join(self.package_folder, "res", "alsa")
        self.runenv_info.define_path("ALSA_CONFIG_DIR", alsa_config_dir)

        # TODO: to remove in conan v2?
        self.cpp_info.names["cmake_find_package"] = "ALSA"
        self.cpp_info.names["cmake_find_package_multi"] = "ALSA"
        self.cpp_info.names["pkg_config"] = "alsa"
        self.env_info.ALSA_CONFIG_DIR = alsa_config_dir
