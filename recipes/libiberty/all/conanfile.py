from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.33.0"


class LibibertyConan(ConanFile):
    name = "libiberty"
    version = "9.1.0"
    description = "A collection of subroutines used by various GNU programs"
    topics = ("conan", "libiberty", "gnu", "gnu-collection")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gcc.gnu.org/onlinedocs/libiberty"
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _libiberty_folder(self):
        return os.path.join(self._source_subfolder, self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libiberty can not be built by Visual Studio.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "gcc"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "libstdc++-v3"))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--enable-install-libiberty",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._libiberty_folder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING.LIB", src=self._libiberty_folder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        self._package_xx(32)
        self._package_xx(64)

    def _package_xx(self, arch):
        lib_arch_dir = os.path.join(self.package_folder, "lib{}".format(arch))
        if os.path.exists(lib_arch_dir):
            libdir = os.path.join(self.package_folder, "lib")
            tools.files.rmdir(self, libdir)
            tools.files.rename(self, lib_arch_dir, libdir)

    def package_info(self):
        self.cpp_info.libs = ["iberty"]
