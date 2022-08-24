from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class JomInstallerConan(ConanFile):
    name = "jom"
    description = "jom is a clone of nmake to support the execution of multiple independent commands in parallel"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://wiki.qt.io/Jom"
    license = "GPL-3.0"
    topics = ("conan", "jom", "build", "makefile", "make")

    settings = "os"

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.download('https://code.qt.io/cgit/qt-labs/jom.git/plain/LICENSE.GPL?h=v%s' % self.version, filename='LICENSE.GPL')

    def package(self):
        self.copy("LICENSE.GPL", dst= 'licenses', src='')
        self.copy("*.exe", dst="bin", src="")
        
    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
