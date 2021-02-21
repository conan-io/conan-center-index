from conans import ConanFile, tools
from conans.tools import check_min_cppstd
import os


class SMLConan(ConanFile):
    name = "sml"
    homepage = "https://github.com/boost-ext/sml"
    description = "SML: C++14 State Machine Library"
    topics = ("state-machine", "metaprogramming", "design-patterns", "sml")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        check_min_cppstd(self, "14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "sml-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*LICENSE.md", dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()
