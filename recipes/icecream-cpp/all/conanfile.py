from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class IcecreamcppConan(ConanFile):
    name = "icecream-cpp"
    license = "MIT"
    homepage = "https://github.com/renatoGarcia/icecream-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A little library to help with the print debugging on C++11 and forward."
    topics = ("debug", "single-header-lib", "print")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

        if self.settings.compiler == "gcc" and tools.scm.Version(self, self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                "icecream-cpp can't be used by {0} {1}".format(
                    self.settings.compiler,
                    self.settings.compiler.version
                )
            )

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("icecream.hpp", dst="include", src=self._source_subfolder)
