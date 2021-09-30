from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class LibsecretConan(ConanFile):
    name = "libsecret"
    description = "A library for storing and retrieving passwords and other secrets"
    topics = ("conan", "libsecret", "gobject", "password", "secret")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wiki.gnome.org/Projects/Libsecret"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"

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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _use_gcrypt(self):
        return self.options.get_safe("with_libgcrypt", False)

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "libsecret recipe is not yet compatible with Windows."
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.settings.os != "Linux":
            # libgcrypt recipe is currently only available on Linux
            del self.options.with_libgcrypt

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd


    def requirements(self):
        self.requires("glib/2.67.2")
        if self._use_gcrypt:
            self.requires("libgcrypt/1.8.4")

    def build_requirements(self):
        self.build_requires("meson/0.56.2")
        self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        defs["introspection"] = False
        defs["manpage"] = False
        defs["gtk_doc"] = False
        defs["gcrypt"] = self._use_gcrypt
        meson.configure(
            defs=defs,
            build_folder=self._build_subfolder,
            source_folder=self._source_subfolder,
            pkg_config_paths=[self.install_folder],
        )
        return meson

    def build(self):
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append({"PKG_CONFIG_PATH": self.install_folder}):
            meson = self._configure_meson()
            meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libsecret-1"
        self.cpp_info.requires = ["glib::glib-2.0", "glib::gobject-2.0"]
        if self._use_gcrypt:
            self.cpp_info.requires.append("libgcrypt::gcrypt")
        self.cpp_info.includedirs = [os.path.join("include", "libsecret-1")]
        self.cpp_info.libs = ["secret-1"]
