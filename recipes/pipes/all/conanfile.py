from conans import ConanFile, tools
import os

class PipesConan(ConanFile):
    name = "pipes"
    description = "Pipelines for expressive code on collections in C++"
    license = "MIT"
    topics = ("pipes", "functional-programming")
    homepage = "https://github.com/joboccara/pipes"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
    def package_id(self):
        self.info.header_only()
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pipes-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"), keep_path=True)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "pipes"
        self.cpp_info.filenames["cmake_find_package_multi"] = "pipes"
        self.cpp_info.names["cmake_find_package"] = "pipes"
        self.cpp_info.names["cmake_find_package_multi"] = "pipes"