import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain

required_conan_version = ">=2"


class SharedMimeInfoConan(ConanFile):
    name = "shared-mime-info"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The freedesktop.org shared MIME database"
    license = "GPL-2.0"
    homepage = "https://gitlab.freedesktop.org/xdg/shared-mime-info"
    topics = ("freedesktop", "mime")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate_build(self):
        check_min_cppstd(self, 17)

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("Only Linux and FreeBSD are supported")

    def requirements(self):
        self.requires("libxml2/[>=2.12.5 <3]")
        self.requires("glib/[>=2.85.3 <3]")

    def build_requirements(self):
        self.tool_requires("meson/1.4.0")
        self.tool_requires("libxml2/<host_version>")
        self.tool_requires("gettext/0.22.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options['build-tools'] = "true"
        tc.project_options['build-translations'] = "false"
        tc.project_options['build-tests'] = "false"
        tc.project_options['update-mimedb'] = "false"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "share", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
