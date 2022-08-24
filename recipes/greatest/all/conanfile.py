from conan import ConanFile, tools


class GreatestConan(ConanFile):
    name = "greatest"
    description = "A C testing library in 1 file. No dependencies, no dynamic allocation."
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/silentbicycle/greatest"
    topics = ("testing", "testing-framework", "unit-testing", "header-only")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("greatest.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
