from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class RobinHoodHashingConan(ConanFile):
    name = "robin-hood-hashing"
    description = "Faster and more efficient replacement for std::unordered_map / std::unordered_set"
    topics = ("robin-hood-hashing", "header-only", "containers")
    homepage = "https://github.com/martinus/robin-hood-hashing"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="robin_hood.h", dst="include",
                  src=os.path.join(self._source_subfolder, "src", "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "robin_hood")
        self.cpp_info.set_property("cmake_target_name", "robin_hood::robin_hood")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "robin_hood"
        self.cpp_info.names["cmake_find_package_multi"] = "robin_hood"
