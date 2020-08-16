import os
from conans import ConanFile, tools


class UtfCppConan(ConanFile):
    name = "utfcpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nemtrif/utfcpp"
    description = "UTF-8 with C++ in a Portable Way"
    settings = "os", "compiler", "arch", "build_type"
    topics = ("utf", "utf8", "unicode", "text")
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.h",
                  dst=os.path.join("include", "utf8cpp"),
                  src=os.path.join(self._source_subfolder, "source"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        # TODO: imported CMake target shouldn't be namespaced
        self.cpp_info.names["cmake_find_package"] = "utf8cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "utf8cpp"
        self.cpp_info.includedirs.append(os.path.join("include", "utf8cpp"))
