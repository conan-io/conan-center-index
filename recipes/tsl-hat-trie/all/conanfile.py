from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class TslHatTrieConan(ConanFile):
    name = "tsl-hat-trie"
    license = "MIT"
    description = "C++ implementation of a fast and memory efficient HAT-trie."
    topics = ("string", "trie", "structure", "hash map", "hash set")
    homepage = "https://github.com/Tessil/hat-trie"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("tsl-array-hash/0.7.1")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "include", "tsl", "array-hash"))
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "include", "tsl", "htrie_hash.h"),
                              '#include "array-hash/', '#include "tsl/')

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tsl-hat-trie")
        self.cpp_info.set_property("cmake_target_name", "tsl::hat_trie")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tsl-hat-trie"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tsl-hat-trie"
        self.cpp_info.names["cmake_find_package"] = "tsl"
        self.cpp_info.names["cmake_find_package_multi"] = "tsl"
        self.cpp_info.components["hat_trie"].names["cmake_find_package"] = "hat_trie"
        self.cpp_info.components["hat_trie"].names["cmake_find_package_multi"] = "hat_trie"
        self.cpp_info.components["hat_trie"].requires = ["tsl-array-hash::array_hash"]
        self.cpp_info.components["hat_trie"].set_property("cmake_target_name", "tsl::hat_trie")
