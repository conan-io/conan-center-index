import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class LDNSConan(ConanFile):
    name = "ldns"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https:///www.nlnetlabs.nl/projects/ldns"
    description = "LDNS is a DNS library that facilitates DNS tool programming"
    topics = ("dns", "rfc", "dnssec")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "openssl/1.1.1k"
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
            ("--enable-shared" if self.option.shared else "--disable-static"),
            ("--enable-static" if not self.option.shared else "--disable-shared"),
            ("--with-pic=yes" if self.options.get_safe("fPIC", True) else "--with-pic=no"),
        ]

        if self.settings.compiler == "apple-clang":
            args.append("--with-xcode-sdk={}".format(tools.XCRun(self.settings).sdk_version))

        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        for target in ["install-h", "install-lib"]:
            autotools.make(target=target)
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["ldns"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["rt", "pthread", "dl"]
