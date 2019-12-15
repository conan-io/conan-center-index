from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class NettleTLS(ConanFile):
    name = "nettle"
    description = "The Nettle and Hogweed low-level cryptographic libraries"
    homepage = "https://www.lysator.liu.se/~nisse/nettle"
    topics = ("conan", "nettle", "crypto", "low-level-cryptographic", "cryptographic")
    license = ("GPL-2.0", "GPL-3.0")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "public_key": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "public_key": True,
    }

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.public_key:
            self.requires("gmp/6.1.2")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Nettle cannot be built using Visual Studio")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("nettle-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ:
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--enable-public-key" if self.options.public_key else "--disable-public-key",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        if self.settings.arch == "x86_64":
            conf_args.append("--enable-x86-aesni")
            if self.version >= "3.5":
                conf_args.append("--enable-x86-sha-ni")
        autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return autotools

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
        self.cpp_info.libs = ["hogweed", "nettle"]
        self.cpp_info.includedirs.append(os.path.join("include", "nettle"))
