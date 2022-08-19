from conan import ConanFile
from conan.tools import files
from conan.tools import build
from conan.errors import ConanInvalidConfiguration
from conans import AutoToolsBuildEnvironment, tools
import os
import textwrap

required_conan_version = ">=1.50.2"


class XorgMacrosConan(ConanFile):
    name = "xorg-macros"
    description = "GNU autoconf macros shared across X.Org projects"
    topics = ("conan", "autoconf", "macros", "build", "system", "m4")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/macros"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def validate(self):
        if build.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("xorg-macros package cannot be cross-compiledyet . Contributions are welcome")

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        self.build_requires("automake/1.16.3")

    def package_id(self):
        self.info.header_only()

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        conf_args = [
            "--datarootdir={}".format(tools.unix_path(self._datarootdir)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        files.apply_conandata_patches(self)
        with files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=self._settings_build.os == "Windows")
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        files.rmdir(self, os.path.join(self._datarootdir, "pkgconfig"))
        files.rmdir(self, os.path.join(self._datarootdir, "util-macros"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "xorg-macros"
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.set_property("pkg_config_custom_content", textwrap.dedent("""\
            datarootdir={datarootdir}
            datadir=${{datarootdir}}
            PACKAGE={name}
            pkgdatadir=${{datadir}}/${{PACKAGE}}
            docdir=${{pkgdatadir}}
        """).format(
            datarootdir=self._datarootdir,
            name="util-macros",
        ))

        aclocal = tools.unix_path(os.path.join(self._datarootdir, "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal)
