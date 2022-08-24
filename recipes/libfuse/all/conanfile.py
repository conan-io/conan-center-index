from conan import ConanFile, tools
from conans import Meson
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class LibfuseConan(ConanFile):
    name = "libfuse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libfuse/libfuse"
    license = "LGPL-2.1"
    description = "The reference implementation of the Linux FUSE interface"
    topics = ("fuse", "libfuse", "filesystem", "linux")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "pkg_config"
    
    _meson = None

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("libfuse supports only Linux and FreeBSD")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("meson/0.59.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.options["examples"] = False
        self._meson.options["utils"] = False
        self._meson.options["tests"] = False
        self._meson.options["useroot"] = False
        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["fuse3"]
        self.cpp_info.includedirs = [os.path.join("include", "fuse3")]
        self.cpp_info.names["pkg_config"] = "fuse3"
        self.cpp_info.system_libs = ["pthread"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "rt"])

