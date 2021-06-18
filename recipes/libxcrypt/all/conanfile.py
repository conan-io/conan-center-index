import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class LibxcryptConan(ConanFile):
    name = "libxcrypt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/besser82/libxcrypt"
    description = "Extended crypt library for descrypt, md5crypt, bcrypt, and others"
    topics = ("conan", "libxcypt", "hash", "password", "one-way", "bcrypt", "md5", "sha256", "sha512")
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
        return os.path.join(self.source_folder, "source_subfolder")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libxcrypt does not support Visual Studio")
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        conf_args = [
            "--disable-werror",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        if self.settings.os == "Windows":
            tools.replace_in_file("libtool", "-DPIC", "")
        return self._autotools

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.am"),
                              "\nlibcrypt_la_LDFLAGS = ", "\nlibcrypt_la_LDFLAGS = -no-undefined ")
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING.LIB", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libcrypt.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["crypt"]
