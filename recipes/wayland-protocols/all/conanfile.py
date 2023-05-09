from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


class WaylandProtocolsConan(ConanFile):
    name = "wayland-protocols"
    description = "Wayland is a project to define a protocol for a compositor to talk to its clients as well as a library implementation of the protocol"
    topics = ("wayland",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/wayland/wayland-protocols"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def build_requirements(self):
        self.tool_requires("meson/1.1.0")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["datadir"] = os.path.join(self.package_folder, "res")
        tc.project_options["tests"] = "false"
        tc.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def _patch_sources(self):
        if Version(self.version) <= "1.23":
            # fixed upstream in https://gitlab.freedesktop.org/wayland/wayland-protocols/-/merge_requests/113
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            "dep_scanner = dependency('wayland-scanner', native: true)",
                            "#dep_scanner = dependency('wayland-scanner', native: true)")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "res", "pkgconfig"))

    def package_info(self):
        pkgconfig_variables = {
            'datarootdir': '${prefix}/res',
            'pkgdatadir': '${datarootdir}/wayland-protocols',
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key,value in pkgconfig_variables.items()))

        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.bindirs = []
