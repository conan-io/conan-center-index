from conans import ConanFile, tools
import os
import glob


class KainjowMustacheConan(ConanFile):
    name = "kainjow-mustache"
    description = "Mustache text templates for modern C++"
    topics = ("conan", "mustache", "template")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kainjow/Mustache"
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(
          "Mustache-{}".format(self.version),
          self._source_subfolder
        )

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("mustache.hpp", dst=os.path.join("include", "kainjow"), src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "kainjow_mustache"
        self.cpp_info.names["cmake_find_package_multi"] = "kainjow_mustache"
