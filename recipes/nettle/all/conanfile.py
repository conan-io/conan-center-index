from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class NettleTLS(ConanFile):
    name = "nettle"
    description = "The Nettle and Hogweed low-level cryptographic libraries"
    homepage = "https://www.lysator.liu.se/~nisse/nettle"
    topics = ("conan", "nettle", "crypto", "low-level-cryptographic", "cryptographic")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "public_key": [True, False],
        "fat": [True, False],
        "x86_aesni": [True, False],
        "x86_shani": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "public_key": True,
        "fat": False,
        "x86_aesni": False,
        "x86_shani": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch != "x86_64":
            del self.options.x86_aesni
            del self.options.x86_shani
        if self.settings.arch != "x86_64" and not str(self.settings.arch).startswith("arm"):
            del self.options.fat

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.public_key:
            self.requires("gmp/6.2.1")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Nettle cannot be built using Visual Studio")
        if tools.Version(self.version) < "3.6" and self.options.get_safe("fat") and self.settings.arch == "x86_64":
            raise ConanInvalidConfiguration("fat support is broken on this nettle release (due to a missing x86_64/sha_ni/sha1-compress.asm source)")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--enable-public-key" if self.options.public_key else "--disable-public-key",
            "--enable-fat" if self.options.get_safe("fat") else "--disable-fat",
            "--enable-x86-aesni" if self.options.get_safe("x86_aesni") else "--disable-x86-aesni",
            "--enable-x86_sshni" if self.options.get_safe("x86_sshni") else "--disable-x86_sshni",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        # srcdir in unix path causes some troubles in asm files on Windows
        if self.settings.os == "Windows":
            tools.replace_in_file(os.path.join(self.build_folder, "config.m4"),
                                  tools.unix_path(os.path.join(self.build_folder, self._source_subfolder)),
                                  os.path.join(self.build_folder, self._source_subfolder).replace("\\", "/"))
        return self._autotools

    def _patch_sources(self):
        makefile_in = os.path.join(self._source_subfolder, "Makefile.in")
        tools.replace_in_file(makefile_in,
                              "SUBDIRS = tools testsuite examples",
                              "SUBDIRS = ")
        # Fix broken tests for compilers like apple-clang with -Werror,-Wimplicit-function-declaration
        tools.replace_in_file(os.path.join(self._source_subfolder, "aclocal.m4"),
                              "cat >conftest.c <<EOF",
                              "cat >conftest.c <<EOF\n#include <stdlib.h>")

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["hogweed"].names["pkgconfig"] = "hogweed"
        self.cpp_info.components["hogweed"].libs = ["hogweed"]
        if self.options.public_key:
            self.cpp_info.components["hogweed"].requires.append("gmp::libgmp")

        self.cpp_info.components["libnettle"].libs = ["nettle"]
        self.cpp_info.components["libnettle"].requires = ["hogweed"]
        self.cpp_info.components["libnettle"].names["pkgconfig"] = "nettle"
