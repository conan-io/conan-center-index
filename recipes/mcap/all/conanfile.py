from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=1.47.0"


class McapConan(ConanFile):
    name = "mcap"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/mcap"
    description = "A C++ implementation of the MCAP file format"
    license = "MIT"
    topics = ("mcap", "serialization", "deserialization", "recording")

    settings = ("os", "compiler", "build_type", "arch")
    generators = ("cmake", "cmake_find_package")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _source_package_path(self):
        return os.path.join(self._source_subfolder, "cpp", "mcap")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("lz4/1.9.3")
        self.requires("zstd/1.5.2")
        if Version(self.version) < "0.1.1":
            self.requires("fmt/8.1.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) <= "11":
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")
        if (self.settings.compiler in ("gcc", "clang")) and Version(self.settings.compiler.version) <= "8":
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")
        if Version(self.version) < "0.1.1" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio compiler support is added in 0.1.1")
        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) < "16":
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_package_path)
        self.copy("include/*", src=self._source_package_path)

    def package_id(self):
        self.info.header_only()
