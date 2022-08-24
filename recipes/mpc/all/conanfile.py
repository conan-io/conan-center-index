from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class MpcConan(ConanFile):
    name = "mpc"
    description = "GNU MPC is a C library for the arithmetic of complex numbers with arbitrarily high precision " \
                  "and correct rounding of the result"
    topics = ("conan", "mpc", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.multiprecision.org/mpc/home.html"
    license = "LGPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("mpfr/4.1.0")

    def validate(self):
        # FIXME: add Visual Studio support, upstream has a makefile.vc
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("mpc can be built with Visual Studio, but it's not supported yet in this recipe.")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = []
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING.LESSER", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["mpc"]
