from conans import ConanFile, tools
import os
import glob

class RangelessConan(ConanFile):
    name = "rangeless"
    description = "c++ LINQ -like library of higher-order functions for data manipulation"
    license = "MIT"
    homepage = "https://github.com/ast-al/rangeless"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("range", "linq", "lazy-evaluation", "header-only")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
