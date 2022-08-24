import os
from conan import ConanFile, tools$


class StcConan(ConanFile):
    name = "stc"
    description = "A modern, user friendly, generic, type-safe and fast C99 container library: String, Vector, Sorted and Unordered Map and Set, Deque, Forward List, Smart Pointers, Bitset and Random numbers."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tylov/STC"
    topics = ("containers", "string", "vector", "map", "set", "deque", "bitset", "random", "list")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package(self):
        if self.version == "1.0.0-rc1":
            self.copy("*.h", dst="include", src=self._source_subfolder, keep_path=True)
        else:
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"), keep_path=True)

        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
