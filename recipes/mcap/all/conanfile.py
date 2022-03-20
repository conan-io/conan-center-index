from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class McapConan(ConanFile):
    name = "mcap"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/mcap"
    description = "A C++ implementation of the MCAP file format"
    license = "Apache-2.0"
    topics = ("mcap", "serialization", "deserialization", "recording")

    settings = ("os", "compiler", "build_type", "arch")
    requires = ("fmt/8.1.1", "lz4/1.9.3", "zstd/1.5.2")
    generators = ("cmake", "cmake_find_package")

    _source_root = "source_root"
    _source_package_path = os.path.join(_source_root, "cpp", "mcap")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_root)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) <= 11:
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")
        if (self.settings.compiler == "gcc" or self.settings.compiler == "clang") and tools.Version(self.settings.compiler.version) <= 8:
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) <= "16.8":
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_package_path)
        self.copy("include/*", src=self._source_package_path)

    def package_id(self):
        self.info.header_only()
