from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import contextlib

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

    def requirements(self):
        if self.options.public_key:
            self.requires("gmp/6.2.1")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Nettle cannot be built using Visual Studio")
        if tools.Version(self.version) < "3.6" and self.options.get_safe("fat") and self.settings.arch == "x86_64":
            raise ConanInvalidConfiguration("fat support is broken on this nettle release (due to a missing x86_64/sha_ni/sha1-compress.asm source)")
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not supported (yet)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build_requirements(self):
        if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ:
            self.build_requires("msys2/cci.latest")

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
        return self._autotools

    def _patch_sources(self):
        makefile_in = os.path.join(self._source_subfolder, "Makefile.in")
        tools.replace_in_file(makefile_in,
                              "SUBDIRS = tools testsuite examples",
                              "SUBDIRS = ")

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["hogweed"].libs = ["hogweed"]
        if self.options.public_key:
            self.cpp_info.components["hogweed"].requires.append("gmp::libgmp")

        self.cpp_info.components["libnettle"].libs = ["nettle"]
        self.cpp_info.components["libnettle"].requires = ["hogweed"]
        self.cpp_info.components["libnettle"].names["pkgconfig"] = ["nettle"]
