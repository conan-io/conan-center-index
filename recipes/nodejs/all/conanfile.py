import os
import sys
from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.errors import ConanInvalidConfiguration


class NodejsInstallerConan(ConanFile):
    name = "nodejs"
    description = "nodejs binaries for use in recipes"
    topics = ("conan", "node", "nodejs")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    license = "MIT"
    settings = "os_build", "arch_build", "compiler", "build_type"
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
                self.run("python configure.py --openssl-no-asm")
                msbuild = MSBuild(self)
                msbuild.build("node.sln", arch=self.settings.arch_build, targets=["node"])
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
                for folder in ["share", "lib", "include"]:
                    tools.rmdir(os.path.join(self.package_folder, folder))

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        bin_dir = self.package_folder if tools.os_info.is_windows else os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bin_dir))
        self.env_info.PATH.append(bin_dir)