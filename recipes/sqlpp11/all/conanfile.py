from conans import ConanFile, tools
import os


class Sqlpp11Conan(ConanFile):
    name = "sqlpp11"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11"
    description = "A type safe SQL template library for C++"
    topics = ("SQL", "DSL", "embedded", "data-base")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("date/2.4.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Sqlpp11"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Sqlpp11"
