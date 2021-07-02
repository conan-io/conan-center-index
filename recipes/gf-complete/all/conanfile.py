from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.33.0"


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
        "neon": [True, False, "auto"],
        "sse": [True, False, "auto"],
        "avx": [True, False, "auto"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "neon": "auto",
        "sse": "auto",
        "avx": "auto"
    }

    _source_subfolder = "source_subfolder"
    _autotools = None

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.sse
            del self.options.avx
        if "arm" not in self.settings.arch:
            del self.options.neon

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os == "Windows" and not self.settings.compiler == "gcc":
            # Building on Windows is currently only supported using the MSYS2
            # subsystem. In theory, the gf-complete library can be build using
            # MSVC. However, some adjustments to the build-system are needed
            # and the CLI tools cannot be build.
            #
            # A suitable profile for MSYS2 can be found in the documentation:
            # https://github.com/conan-io/docs/blob/b712aa7c0dc99607c46c57585787ced2ae66ac33/systems_cross_building/windows_subsystems.rst
            raise ConanInvalidConfiguration("Windows is only supported using the MSYS2 subsystem")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=bool(self.settings.os == "Windows"))

        with tools.environment_append(self._autotools.vars):
            with tools.chdir(self._source_subfolder):
                self.run("./autogen.sh", win_bash=bool(self.settings.os == "Windows"))

        if "x86" in self.settings.arch:
            self._autotools.flags.append('-mstackrealign')

        configure_args = [
            "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
            "--enable-static=%s" % ("no" if self.options.shared else "yes")
        ]

        if "arm" in self.settings.arch:
            if self.options.neon != "auto":
                configure_args.append("--{}-neon".format(
                    "enable" if self.options.neon else "disable"))

        if self.settings.arch in ["x86", "x86_64"]:
            if self.options.sse != "auto":
                configure_args.append("--{}-sse".format(
                    "enable" if self.options.sse else "disable"))

            if self.options.avx != "auto":
                configure_args.append("--{}-avx".format(
                    "enable" if self.options.avx else "disable"))

        self._autotools.configure(args=configure_args,
                                  configure_dir=self._source_subfolder)

        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        # don't package la file
        la_file = os.path.join(self.package_folder, "lib", "libgf_complete.la")
        if os.path.isfile(la_file):
            os.unlink(la_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
