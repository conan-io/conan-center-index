from conans import ConanFile, tools
import os
import glob

class RangelessConan(ConanFile):
    name = "rangeless"
    license = "Public domain"
    homeback = "https://github.com/ast-al/rangeless"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("range", "linq", "lazy-evaluation", "header-only")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
    def package_id(self):
        self.info.header_only()
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)
    
    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
