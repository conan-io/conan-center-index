from conans import ConanFile, tools
import os


class VariantConan(ConanFile):
    name = "mpark-variant"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mpark/variant"
    description = "C++17 std::variant for C++11/14/17"
    license = "BSL-1.0"
    topics = ("conan", "variant", "mpark-variant")
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "variant-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        # TODO: CMake imported target shouldn't be namespaced (waiting https://github.com/conan-io/conan/issues/7615 to be implemented)
        self.cpp_info.names["cmake_find_package"] = "mpark_variant"
        self.cpp_info.names["cmake_find_package_multi"] = "mpark_variant"
