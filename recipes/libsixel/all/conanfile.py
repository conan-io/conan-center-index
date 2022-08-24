import os
import functools
from conans import ConanFile, Meson, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.33.0"

class LibSixelConan(ConanFile):
    name = "libsixel"
    description = "A SIXEL encoder/decoder implementation derived from kmiya's sixel (https://github.com/saitoha/sixel)."
    topics = ("sixel")
    license = "MIT"
    homepage = "https://github.com/libsixel/libsixel"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_curl": [True, False],
        "with_gdk_pixbuf2": [True, False],
        "with_gd": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_curl": True,
        "with_gd": False,
        "with_gdk_pixbuf2": False,
        "with_jpeg": True,
        "with_png": True,
    }
    generators = "cmake", "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")
        if is_msvc(self):
            raise ConanInvalidConfiguration("{}/{} does not support Visual Studio".format(self.name, self.version))

    def build_requirements(self):
        self.build_requires("meson/0.62.2")
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        if self.options.with_curl:
            self.requires("libcurl/7.83.1")
        if self.options.with_gd:
            self.requires("libgd/2.3.2")
        if self.options.with_gdk_pixbuf2:
            self.requires("gdk-pixbuf/2.42.6")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        defs = {
            "libcurl": "enabled" if self.options.with_curl else "disabled",
            "gd": "enabled" if self.options.with_gd else "disabled",
            "gdk-pixbuf2": "enabled" if self.options.with_gdk_pixbuf2 else "disabled",
            "img2sixel": "disabled",
            "sixel2png": "disabled",
            "python2": "disabled",
        }
        meson.configure(
            defs=defs,
            source_folder=self._source_subfolder,
        )
        return meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["sixel"]
