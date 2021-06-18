import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class IcecreamcppConan(ConanFile):
    name = "icecream-cpp"
    license = "MIT"
    homepage = "https://github.com/renatoGarcia/icecream-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A little library to help with the print debugging on C++11 and forward."
    topics = ("debug", "single-header-lib", "print")
    settings = ("compiler", )
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('icecream-cpp-{}'.format(self.version), self._source_subfolder)

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, minimal_cpp_standard)

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                "icecream-cpp can't be used by {0} {1}".format(
                    self.settings.compiler,
                    self.settings.compiler.version
                )
            )

    def package(self):
        self.copy('LICENSE.txt', dst='licenses', src=self._source_subfolder)
        self.copy('icecream.hpp', dst='include', src=self._source_subfolder)
