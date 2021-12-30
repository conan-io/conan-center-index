import os

from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class TllistConan(ConanFile):
    name = "tllist"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codeberg.org/dnkl/tllist"
    description = "A C header file only implementation of a typed linked list."
    topics = ("list", "utils", "tllist")
    generators = ("pkg_config")
    settings = "os", "arch", "build_type"
    no_copy_source = True
    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")

    def build_requirements(self):
        self.build_requires("pkgconf/[>=1.7.4]")
        self.build_requires("meson/[>=0.60.0]")
        self.build_requires("ninja/[>=1.10.0]")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.configure(source_folder=self._source_subfolder)
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()
        meson.test()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include"))

