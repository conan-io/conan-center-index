from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class WaylandProtocolsConan(ConanFile):
    name = "wayland-protocols"
    description = "The Wayland-Protocols package contains additional Wayland protocols that add functionality outside of protocols already in the Wayland core."
    topics = ("conan", "wayland-protocols", "wayland")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wayland.freedesktop.org/"
    license = "MIT"
    generators = "pkg_config"

    settings = []
    options = {}
    default_options = {}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None

    build_requires = (
        "wayland/1.18.0"
    )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir= self._source_subfolder,
                                    args=['--datadir=%s' % os.path.join(self.package_folder, "res")])
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "res", "pkgconfig"))

    def package_info(self):
        pass

