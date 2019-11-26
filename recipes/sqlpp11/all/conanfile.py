from conans import ConanFile, tools
import os


class Sqlpp11Conan(ConanFile):
    name = "sqlpp11"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11"
    description = "A type safe SQL template library for C++"
    generators = "cmake"
    topics = ("SQL", "DSL", "embedded", "data-base")
    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("date/2.4.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        self.copy("include/*", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
