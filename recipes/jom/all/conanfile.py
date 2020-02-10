from conans import ConanFile, tools
import os


class JomInstallerConan(ConanFile):
    name = "jom"
    description = "jom is a clone of nmake to support the execution of multiple independent commands in parallel"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://wiki.qt.io/Jom"
    license = "GPL-3.0"

    settings = {"os" : ["Windows"]}

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.download('https://code.qt.io/cgit/qt-labs/jom.git/plain/LICENSE.GPL?h=v%s' % self.version, filename='LICENSE.GPL')

    def package(self):
        self.copy("LICENSE.GPL", dst= 'licenses', src='')
        self.copy("*.exe", dst="bin", src="")
        
    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
