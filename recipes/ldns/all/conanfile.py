from conans import ConanFile, tools, AutoToolsBuildEnvironment
import glob
import os

class ldnsConan(ConanFile):
    name = "ldns"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nlnetlabs.nl/projects/ldns"
    description = "LDNS is a DNS library that facilitates DNS tool programming"
    topics = ("DNS")

    settings = "os", "compiler", "build_type", "arch"
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

    def requirements(self):
        self.requires("openssl/1.1.1o")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        yes_no = lambda v: "yes" if v else "no"

        args = [
            # libraries
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-pic={}".format(yes_no(self.settings.os != "Windows" and (self.options.shared or self.options.fPIC))),
            "--disable-rpath",
            # dependencies
            "--with-ssl={}".format(self.deps_cpp_info["openssl"].rootpath),
            # DNSSEC algorithm support
            "--enable-ecdsa",
            "--enable-ed25519",
            "--enable-ed448",
            "--disable-dsa",
            "--disable-gost",
            "--enable-full-dane",
            # tooling
            "--disable-ldns-config",
            "--without-drill",
            "--without-examples",
            # library bindings
            "--without-pyldns",
            "--without-p5-dns-ldns",
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
        autotools = self._configure_autotools()
        for target in ["install-h", "install-lib"]:
            autotools.make(target=target)
        for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
            os.remove(la_file)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["ldns"]
