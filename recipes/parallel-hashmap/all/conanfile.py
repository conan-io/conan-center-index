from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class ParallelHashmapConan(ConanFile):
    name = "parallel-hashmap"
    description = "A family of header-only, very fast and memory-friendly hashmap and btree containers."
    license = "Apache-2.0"
    topics = ("conan", "parallel-hashmap", "parallel", "hashmap", "btree")
    homepage = "https://github.com/greg7mdp/parallel-hashmap"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h",
                  dst=os.path.join("include", "parallel_hashmap"),
                  src=os.path.join(self._source_subfolder, "parallel_hashmap"))
        self.copy("phmap.natvis", dst="res", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "phmap"
        self.cpp_info.names["cmake_find_package_multi"] = "phmap"
