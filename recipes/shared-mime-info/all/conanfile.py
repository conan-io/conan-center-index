from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.system.package_manager import Apt, Yum, PacMan, Zypper

import os

required_conan_version = ">=1.55.0"


class SharedMimeInfoConan(ConanFile):
    name = "shared-mime-info"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The freedesktop.org shared MIME database"
    license = ("GPL-2")
    homepage = "https://gitlab.freedesktop.org/xdg/shared-mime-info"
    topics = ("ferrdesktop", "mime")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("OS is not supported")

    def package_id(self):
        del self.info.settings.build_type
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = MesonToolchain(self)
        tc.generate()

    def build(self):
        if self.settings.os == "Linux":
            Apt(self).install(["libxml2-utils"])

        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder,"licenses"))

        meson = Meson(self)
        meson.install()
