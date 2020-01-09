import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class NodejsInstallerConan(ConanFile):
    name = "nodejs"
    description = "nodejs binaries for use in recipes"
    topics = ("conan", "node", "nodejs")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    license = "MIT"
    settings = "os_build", "arch_build", "compiler"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.os_build == "Windows" and self.settings.compiler == "Visual Studio"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "node-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._autotools.configure()
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            if self._is_msvc:
                self.run("vcbuild.bat")
            else:
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            if self._is_msvc:
                # TODO
                pass
            else:
                autotools = self._configure_autotools()
                autotools.install()

    def package_info(self):
        bin_dir = self.package_folder if tools.os_info.is_windows else os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bin_dir))
        self.env_info.PATH.append(bin_dir)