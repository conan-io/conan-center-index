import os

from conans import ConanFile, tools


class IcecreamcppConan(ConanFile):
    name = "icecream-cpp"
    license = "MIT"
    homepage = "https://github.com/renatoGarcia/icecream-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A little library to help with the print debugging on C++11 and forward."
    topics = ("debug", "single-header-lib", "print")
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('icecream-cpp-{}'.format(self.version), self._source_subfolder)

    def package(self):
        self.copy('LICENSE.txt', dst='licenses', src=self._source_subfolder)
        self.copy('icecream.hpp', dst='include', src=self._source_subfolder)
