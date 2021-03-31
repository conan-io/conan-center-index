from conans import ConanFile, tools
import os
import glob


class ReflCppConan(ConanFile):
    name = "refl-cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/veselink1/refl-cpp"
    description = "A modern compile-time reflection library for C++ with support for overloads, templates, attributes and proxies "
    topics = ("header", "header-only", "reflection", "modern", "metaprogramming")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = self._source_subfolder
        self.copy(pattern="*.hpp", dst="include", src=include_folder)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
