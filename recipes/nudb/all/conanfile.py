import os
from conans import ConanFile, tools

required_conan_version = ">=1.33.0"

class NudbConan(ConanFile):
    name = "nudb"
    license = "BSL-1.0"
    description = "A fast key/value insert-only database for SSD drives in C++11"
    homepage = "https://github.com/CPPAlliance/NuDB"
    url = "https://github.com/conan-io/conan-center-index/"
    topics = ("header-only", "KVS", "insert-only")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.78.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "NuDB", "include"), dst="include")
        self.copy("*.ipp", src=os.path.join(self._source_subfolder, "NuDB", "include"), dst="include")
        self.copy("LICENSE_1_0.txt ", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()
