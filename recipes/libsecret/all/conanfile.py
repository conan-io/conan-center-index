from conans import ConanFile, Meson, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibsecretConan(ConanFile):
    name = "libsecret"
    description = "A library for storing and retrieving passwords and other secrets"
    topics = ("libsecret", "gobject", "password", "secret")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wiki.gnome.org/Projects/Libsecret"
    license = "LGPL-2.1-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libgcrypt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libgcrypt": True,
    }

    generators = "pkg_config"
    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _use_gcrypt(self):
        return self.options.get_safe("with_libgcrypt", False)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            # libgcrypt recipe is currently only available on Linux
            del self.options.with_libgcrypt

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("glib/2.70.1")
        if self._use_gcrypt:
            self.requires("libgcrypt/1.8.4")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "libsecret recipe is not yet compatible with Windows."
            )

    def build_requirements(self):
        self.build_requires("meson/0.60.2")
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        defs = {}
        defs["introspection"] = False
        defs["manpage"] = False
        defs["gtk_doc"] = False
        defs["gcrypt"] = self._use_gcrypt
        self._meson.configure(
            defs=defs,
            build_folder=self._build_subfolder,
            source_folder=self._source_subfolder,
            pkg_config_paths=[self.install_folder],
        )
        return self._meson

    def build(self):
        with tools.run_environment(self):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.run_environment(self):
            meson = self._configure_meson()
            meson.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libsecret-1"
        self.cpp_info.requires = ["glib::glib-2.0", "glib::gobject-2.0"]
        if self._use_gcrypt:
            self.cpp_info.requires.append("libgcrypt::libgcrypt")
        self.cpp_info.includedirs = [os.path.join("include", "libsecret-1")]
        self.cpp_info.libs = ["secret-1"]
