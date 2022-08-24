from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibxcryptConan(ConanFile):
    name = "libxcrypt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/besser82/libxcrypt"
    description = "Extended crypt library for descrypt, md5crypt, bcrypt, and others"
    topics = ("libxcypt", "hash", "password", "one-way", "bcrypt", "md5", "sha256", "sha512")
    license = ("LGPL-2.1-or-later", )
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libxcrypt does not support Visual Studio")

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-werror",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        if self.settings.os == "Windows":
            tools.files.replace_in_file(self, "libtool", "-DPIC", "")
        return self._autotools

    def build(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.am"),
                              "\nlibcrypt_la_LDFLAGS = ", "\nlibcrypt_la_LDFLAGS = -no-undefined ")
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING.LIB", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libxcrypt"
        self.cpp_info.libs = ["crypt"]
