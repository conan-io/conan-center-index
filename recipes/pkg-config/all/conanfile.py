from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class PkgConfigConan(ConanFile):
    name = "pkg-config"
    description = "The pkg-config program is used to retrieve information about installed libraries in the system"
    topics = ("conan", "pkg-config", "package config")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/pkg-config/"
    license = "GPL-2.0-or-later"
    settings = "os_build", "arch_build", "compiler"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _autotools = None

    @property
    def _is_mingw_windows(self):
        return self.settings.os_build == "Windows" and self.settings.compiler == "gcc" and os.name == "nt"

    def build_requirements(self):
        if self._is_mingw_windows and "CONAN_BASH_PATH" not in os.environ and \
           tools.os_info.detect_windows_subsystem() != 'msys2':
            self.build_requires("msys2/20190524")

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("builds with Visual Studio aren't currently supported, "
                                            "use MinGW instead to build for Windows")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pkg-config-" + self.version, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            # http://www.linuxfromscratch.org/lfs/view/systemd/chapter06/pkg-config.html
            args = ["--with-internal-glib", "--disable-host-tool"]
            self._autotools = AutoToolsBuildEnvironment(self, self._is_mingw_windows)
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        if self._is_mingw_windows:
            package_folder = tools.unix_path(os.path.join(self.package_folder, "bin"))
            tools.run_in_windows_bash(self, "cp $(which libwinpthread-1.dll) {}".format(package_folder))
        tools.rmdir(os.path.join(self.package_folder, 'share'))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)
