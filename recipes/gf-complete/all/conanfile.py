from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class GfCompleteConan(ConanFile):
    name = "gf-complete"
    description = "A library for Galois Field arithmetic"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ceph/gf-complete"
    license = "BSD-3-Clause"
    topics = ("galois field", "math", "algorithms")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "neon": [True, False],
        "sse": [True, False],
        "avx": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "neon": True,
        "sse": True,
        "avx": False
    }

    _source_subfolder = "source_subfolder"
    _autotools = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=tools.os_info.is_windows)

        with tools.environment_append(self._autotools.vars):
            # run autoreconf
            self.run("./autogen.sh", win_bash=tools.os_info.is_windows)

        if "x86" in self.settings.arch:
            self._autotools.flags.append('-mstackrealign')

        if "fPIC" in self.options:
            self._autotools.fpic = self.options.fPIC

        configure_args = [
            "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
            "--enable-static=%s" % ("no" if self.options.shared else "yes")
        ]

        # enabled by default
        if not self.options.neon:
            configure_args.append("--disable-neon")
        if not self.options.sse:
            configure_args.append("--disable-sse")

        # disabled by default
        if self.options.avx:
            configure_args.append("--enable-avx")

        self._autotools.configure(args=configure_args)

        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

        # don't package la file
        la_file = os.path.join(self.package_folder, "lib", "libgf_complete.la")
        if os.path.isfile(la_file):
            os.unlink(la_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include"))
