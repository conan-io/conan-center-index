from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path, unix_path_package_info_legacy
import os
import textwrap

required_conan_version = ">=1.53.2"


class XorgMacrosConan(ConanFile):
    name = "xorg-macros"
    description = "GNU autoconf macros shared across X.Org projects"
    topics = ("autoconf", "macros", "build", "system", "m4")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/macros"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"

    def layout(self):
        basic_layout(self)

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.build_requires("msys2/cci.latest")
        self.build_requires("automake/1.16.3")

    def package_id(self):
        self.info.clear()

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def generate(self):
        tc = AutotoolsToolchain(self)
        conf_args = [
            f"--datarootdir={unix_path(self._datarootdir)}",
        ]
        tc.configure_args(args=conf_args)

    def build(self):
        apply_conandata_patches(self)
        with files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=self._settings_build.os == "Windows")
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst="licenses")
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self._datarootdir, "pkgconfig"))
        rmdir(self, os.path.join(self._datarootdir, "util-macros"))

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

        aclocal = unix_path_package_info_legacy(os.path.join(self._datarootdir, "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal)
