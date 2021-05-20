from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibbacktraceConan(ConanFile):
    name = "libbacktrace"
    description = "A C library that may be linked into a C/C++ program to produce symbolic backtraces."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ianlancetaylor/libbacktrace"
    license = "BSD-3-Clause"
    topics = ("conan", "backtrace", "stack-trace")

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libbacktrace can't be built with Visual Studio")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.options.shared:
            args = ["--enable-shared", "--disable-static"]
        else:
            args = ["--disable-shared", "--enable-static"]
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["backtrace"]
