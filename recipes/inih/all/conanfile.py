from conans import ConanFile, tools
from conan.tools.meson import MesonToolchain, Meson
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class InihConan(ConanFile):
    name = "inih"
    description = "Simple .INI file parser in C, good for embedded systems "
    license = "BSD-3-Clause"
    topics = ("conan", "inih", "ini", "configuration", "parser")
    homepage = "https://github.com/benhoyt/inih"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared inih is not supported on Windows")

    def build_requirements(self):
        self.build_requires("meson/0.59.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.definitions["distro_install"] = True
        tc.generate()

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self, build_folder=self._build_subfolder)
        self._meson.configure(source_folder=self._source_subfolder)
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.settings.compiler == "Visual Studio":
            # https://github.com/mesonbuild/meson/issues/7378
            tools.rename(os.path.join(self.package_folder, "lib", "libinih.a"),
                         os.path.join(self.package_folder, "lib", "inih.lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "inih"
        self.cpp_info.libs = ["inih"]
