from conans import ConanFile, tools
import os


class BoolinqConan(ConanFile):
    name = "boolinq"
    description = "Super tiny C++11 single-file header-only LINQ template library"
    topics = ("conan", "boolinq", "linq", "header-only")
    license = "MIT"
    homepage = "https://github.com/k06a/boolinq"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
