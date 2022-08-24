from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"


class BoolinqConan(ConanFile):
    name = "boolinq"
    description = "Super tiny C++11 single-file header-only LINQ template library"
    topics = ("boolinq", "linq", "header-only")
    license = "MIT"
    homepage = "https://github.com/k06a/boolinq"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
