import glob
import os
import os.path
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class ldnsConan(ConanFile):
    name = "ldns"
    version = "1.7.1"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https:///www.nlnetlabs.nl/projects/ldns"
    description = "LDNS is a DNS library that facilitates DNS tool programming"
    topics = ("DNS")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    requires = "openssl/1.1.1j"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ldns-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        if self.options.shared:
            shared = "--enable-shared"
            static = "--disable-static"
        else:
            shared = "--disable-shared"
            static = "--enable-static"

        if self.settings.os != "Windows":
            if self.options.shared or self.options.fPIC:
                pic = "--with-pic=yes"
            else:
                pic = "--with-pic=no"

        args = [
            "--with-ssl={}".format(self.deps_cpp_info["openssl"].rootpath),
            "--disable-ldns-config",
            "--disable-rpath", shared, static, pic,
            # DNSSEC algorithm support
            "--enable-dsa",
            "--enable-ecdsa",
            "--enable-ed25519",
            "--enable-ed448",
            "--disable-gost",
            "--enable-full-dane",
            # tooling
            "--without-drill",
            "--without-examples",
            # library bindings
            "--without-pyldns",
            "--without-p5-dns-ldns",
        ]

        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        for target in ["install-h", "install-lib"]:
            autotools.make(target=target)
        for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
            os.remove(la_file)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["ldns"]
