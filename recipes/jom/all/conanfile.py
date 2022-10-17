from conan import ConanFile
from conan.tools.files import get, download
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.47.0"

class JomInstallerConan(ConanFile):
    name = "jom"
    description = "jom is a clone of nmake to support the execution of multiple independent commands in parallel"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://wiki.qt.io/Jom"
    license = "GPL-3.0"
    topics = ("build", "makefile", "make")

    settings = "os", "arch", "compiler", "build_type"

    # not needed but supress warning message from conan commands
    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        download(self, f'https://code.qt.io/cgit/qt-labs/jom.git/plain/LICENSE.GPL?h=v{self.version}', filename='LICENSE.GPL')

    def package(self):
        self.copy("LICENSE.GPL", dst= 'licenses', src='')
        self.copy("*.exe", dst="bin", src="")

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        # In case need to find packaged tools when building a package
        self.buildenv_info.append("PATH", bin_folder)
        # In case need to find packaged tools at runtime
        self.runenv_info.append("PATH", bin_folder)
        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(bin_folder)
