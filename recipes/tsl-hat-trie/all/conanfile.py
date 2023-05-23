from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class TslHatTrieConan(ConanFile):
    name = "tsl-hat-trie"
    license = "MIT"
    description = "C++ implementation of a fast and memory efficient HAT-trie."
    topics = ("string", "trie", "structure", "hash map", "hash set")
    homepage = "https://github.com/Tessil/hat-trie"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tsl-array-hash/0.7.1")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        rmdir(self, os.path.join(self.source_folder, "include", "tsl", "array-hash"))
        replace_in_file(self, os.path.join(self.source_folder, "include", "tsl", "htrie_hash.h"),
                              '#include "array-hash/', '#include "tsl/')

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tsl-hat-trie")
        self.cpp_info.set_property("cmake_target_name", "tsl::hat_trie")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tsl-hat-trie"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tsl-hat-trie"
        self.cpp_info.names["cmake_find_package"] = "tsl"
        self.cpp_info.names["cmake_find_package_multi"] = "tsl"
        self.cpp_info.components["hat_trie"].names["cmake_find_package"] = "hat_trie"
        self.cpp_info.components["hat_trie"].names["cmake_find_package_multi"] = "hat_trie"
        self.cpp_info.components["hat_trie"].requires = ["tsl-array-hash::array_hash"]
        self.cpp_info.components["hat_trie"].set_property("cmake_target_name", "tsl::hat_trie")
        self.cpp_info.components["hat_trie"].bindirs = []
        self.cpp_info.components["hat_trie"].libdirs = []
        self.cpp_info.components["hat_trie"].resdirs = []
