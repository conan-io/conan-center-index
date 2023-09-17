from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path_package_info_legacy
import os
import textwrap

required_conan_version = ">=1.57"


class XorgMacrosConan(ConanFile):
    name = "xorg-macros"
    description = "GNU autoconf macros shared across X.Org projects"
    topics = ("autoconf", "macros", "build", "system", "m4")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/macros"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        self.tool_requires("automake/1.16.5")

    def package_id(self):
        self.info.clear()

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend(
            ["--datarootdir=${prefix}/bin/share"]
        )
        tc.generate()

        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
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

        aclocal = os.path.join(self._datarootdir, "aclocal")
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal)

        # TODO: remove once recipe only supports Conan >= 2.0 only
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(unix_path_package_info_legacy(self, aclocal ))
