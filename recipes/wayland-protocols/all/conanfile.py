from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conans import Meson, tools
import os

required_conan_version = ">=1.33.0"


class WaylandProtocolsConan(ConanFile):
    name = "wayland-protocols"
    description = "Wayland is a project to define a protocol for a compositor to talk to its clients as well as a library implementation of the protocol"
    topics = ("wayland")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/wayland/wayland-protocols"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"

    _meson = None

    def package_id(self):
        self.info.header_only()

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Wayland-protocols can be built on Linux only")

    def build_requirements(self):
        self.build_requires("meson/0.63.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        if tools.Version(self.version) <= 1.23:
            # fixed upstream in https://gitlab.freedesktop.org/wayland/wayland-protocols/-/merge_requests/113
            tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                                  "dep_scanner = dependency('wayland-scanner', native: true)",
                                  "#dep_scanner = dependency('wayland-scanner', native: true)")

    def _configure_meson(self):
        if not self._meson:
            defs = {
                "tests": "false",
            }
            self._meson = Meson(self)
            self._meson.configure(
                source_folder=self._source_subfolder,
                build_folder=self._build_subfolder,
                defs=defs,
                args=[f'--datadir={self.package_folder}/res'],
            )
        return self._meson

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "res", "pkgconfig"))

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
