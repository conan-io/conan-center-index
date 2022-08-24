from conans import AutoToolsBuildEnvironment, ConanFile, tools
import functools
import os

required_conan_version = ">=1.33.0"


class GtkDocStubConan(ConanFile):
    name = "gtk-doc-stub"
    homepage = "https://gitlab.gnome.org/GNOME/gtk-doc-stub"
    description = "Helper scripts for generating GTK documentation"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-2.0-or-later"
    topics = ("gtk", "documentation", "gtkdocize")
    settings = "os"

    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = [
            "--datadir={}".format(tools.microsoft.unix_path(self, os.path.join(self.package_folder, "res"))),
            "--datarootdir={}".format(tools.microsoft.unix_path(self, os.path.join(self.package_folder, "res"))),
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        automake_dir = tools.microsoft.unix_path(self, os.path.join(self.package_folder, "res", "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(automake_dir))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(automake_dir)
