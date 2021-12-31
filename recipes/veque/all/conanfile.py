import os
from conans import ConanFile, tools


class VequeConan(ConanFile):
    name = "veque"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Shmoopty/veque"
    description = "Fast C++ container combining the best features of std::vector and std::deque"
    topics = ("cpp17", "vector", "deque")
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

