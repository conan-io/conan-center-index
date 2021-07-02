import os

from conans import ConanFile, tools

class ConanRecipe(ConanFile):
    name = "robin-hood-hashing"
    description = "Faster and more efficient replacement for std::unordered_map / std::unordered_set"
    topics = ("conan", "robin-hood-hashing", "header-only", "containers")
    homepage = "https://github.com/martinus/robin-hood-hashing"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "compiler"

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)

        self.copy(pattern="robin_hood.h", dst="include",
                  src=os.path.join(self._source_subfolder, "src", "include"))

    def package_info(self):
        # Original CMakeLists.txt exports "robin_hood::robin_hood" target:
        self.cpp_info.names["cmake_find_package"] = "robin_hood"
        self.cpp_info.names["cmake_find_package_multi"] = "robin_hood"

    def package_id(self):
        self.info.header_only()

