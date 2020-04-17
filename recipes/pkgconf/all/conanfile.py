from conans import ConanFile, Meson, tools
import os


class PkgConfConan(ConanFile):
    name = "pkgconf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pkgconf.org/"
    topics = ("conan", "pkgconf")
    settings = "os", "arch", "compiler", "build_type"
    license = "ISC"
    description = "package compiler and linker metadata toolkit"
    exports_sources = "patches/**"

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pkgconf-pkgconf-{}".format(self.version), self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not tools.which("meson"):
            self.build_requires("meson/0.53.2")

    @property
    def _sharedstatedir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.build_type = "Release"
        self._meson.options["default_library"] = "static"
        self._meson.options["tests"] = False
        self._meson.options["sharedstatedir"] = self._sharedstatedir
        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                              "shared_library(", "library(")
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                              "'-DLIBPKGCONF_EXPORT'",
                              "['-DLIBPKGCONF_EXPORT', '-DPKGCONFIG_IS_STATIC']")

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        meson = self._meson
        meson.install()

        tools.rmdir(os.path.join(self.package_folder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "share", "man"))
        os.rename(os.path.join(self.package_folder, "share", "aclocal"),
                  os.path.join(self.package_folder, "bin", "aclocal"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        pkg_config = os.path.join(bindir, "pkgconf").replace("\\", "/")
        self.output.info("Setting PKG_CONFIG env var: {}".format(pkg_config))
        self.env_info.PKG_CONFIG = pkg_config

        automake_extra_includes = os.path.join(self.package_folder , "bin", "aclocal").replace("\\", "/")
        self.output.info("Appending AUTOMAKE_EXTRA_INCLUDES env var: {}".format(automake_extra_includes))
        self.env_info.AUTOMAKE_EXTRA_INCLUDES.append(automake_extra_includes)
