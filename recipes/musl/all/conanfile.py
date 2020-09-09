import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class MuslConan(ConanFile):
    name = "musl"
    description = "musl is an implementation of the C standard library built on top of the Linux system call API, " \
                  "including interfaces defined in the base language standard, POSIX, and widely agreed-upon " \
                  "extensions."
    homepage = "https://musl.libc.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "musl", "libc")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("musl is only supported on Linux.")
        if self.settings.compiler != ["gcc", "clang"]:
            raise ConanInvalidConfiguration("musl is only supported on Linux.")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = []
        if self.settings.compiler == "gcc":
            conf_args.append("--enable-wrapper=gcc")
        elif self.settings.compiler == "clang":
            conf_args.append("--enable-wrapper=clang")
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        musl_cc = None
        musl_cxx = None
        musl_ld = None

        if self.settings.compiler == "gcc":
            musl_cc = os.path.join(self.package_folder, "bin", "musl-gcc") + " -static"
            musl_cxx = musl_cc
            musl_ld = musl_cc
        elif self.settings.compiler == "clang":
            musl_cc = os.path.join(self.package_folder, "bin", "musl-clang") + " -static"
            musl_cxx = musl_cc
            musl_ld = os.path.join(self.package_folder, "bin", "ld.musl-clang")

        if musl_cc is not None:
            self.output.info("Setting CC to '{}'".format(musl_cc))
            self.env_info.CC = musl_cc
        if musl_cxx is not None:
            self.output.info("Setting CXX to '{}'".format(musl_cxx))
            self.env_info.CXX = musl_cxx
        if musl_ld is not None:
            self.output.info("Setting LD to '{}'".format(musl_ld))
            self.env_info.CXX = musl_ld
