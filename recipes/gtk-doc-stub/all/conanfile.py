from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path

import os

required_conan_version = ">=1.53.0"


class GtkDocStubConan(ConanFile):
    name = "gtk-doc-stub"
    homepage = "https://gitlab.gnome.org/GNOME/gtk-doc-stub"
    description = "Helper scripts for generating GTK documentation"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-2.0-or-later"
    topics = ("gtk", "documentation", "gtkdocize")
    package_type = "application"
    settings = "os"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--datarootdir=${prefix}/res")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        automake_dir = unix_path(self, os.path.join(self.package_folder, "res", "aclocal"))
        self.buildenv_info.append_path("AUTOMAKE_CONAN_INCLUDES", automake_dir)

        # TODO: remove the following when only Conan 2.0 is supported
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(automake_dir)
