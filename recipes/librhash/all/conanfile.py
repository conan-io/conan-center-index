import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class LibRHashConan(ConanFile):
    name = "librhash"
    description = "Great utility for computing hash sums"
    topics = ("conan", "rhash", "hash", "checksum")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://rhash.sourceforge.net/"
    license = "MIT"
    exports_sources = "CMakeLists.txt",
    generators = "cmake",
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }

    _autotools = None
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported")
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20190524")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1i")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "RHash-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--enable-openssl" if self.options.with_openssl else "--disable-openssl",
            "--disable-gettext",
            # librhash's configure script is custom and does not understand "--bindir=${prefix}/bin" arguments
            "--prefix={}".format(tools.unix_path(self.package_folder)),
            "--bindir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin"))),
            "--libdir={}".format(tools.unix_path(os.path.join(self.package_folder, "lib"))),
            "--extra-cflags={}".format(self._autotools.vars["CPPFLAGS"]),
            "--extra-ldflags={}".format(self._autotools.vars["LDFLAGS"]),
        ]
        if self.options.shared:
            conf_args.extend(["--enable-lib-shared", "--disable-lib-static"])
        else:
            conf_args.extend(["--disable-lib-shared", "--enable-lib-static"])

        self._autotools.configure(args=conf_args, use_default_install_dirs=False)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
            autotools.make(target="install-lib-headers")
            with tools.chdir("librhash"):
                if self.options.shared:
                    autotools.make(target="install-so-link")
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibRHash"
        self.cpp_info.names["cmake_find_package_multi"] = "LibRHash"
        self.cpp_info.libs = tools.collect_libs(self)
