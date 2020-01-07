from conans import ConanFile, tools
import os


class AutoMakeBuildAuxConan(ConanFile):
    name = "automake_build_aux"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    description = "auxiliary build files from automake distribution: compiler and ar-lib"
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("automake-" + self.version, self._source_subfolder)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="compile", src=os.path.join(self._source_subfolder, "lib"), dst='bin')
        self.copy(pattern="ar-lib", src=os.path.join(self._source_subfolder, "lib"), dst='bin')

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, 'bin'))
