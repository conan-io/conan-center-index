from conans import ConanFile, tools
import os


class GreatestConan(ConanFile):
    name = "greatest"
    description = "A C testing library in 1 file. No dependencies, no dynamic allocation."
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/silentbicycle/greatest"
    topics = ("conan", "testing", "testing-framework", "unit-testing", "header-only")
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "{0}-{1}".format(self.name, self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("greatest.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
