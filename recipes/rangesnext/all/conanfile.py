from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class RangesnextConan(ConanFile):
    name = "rangesnext"
    description = "ranges features for C++23 ported to C++20"
    topics = ("conan", "rangesnext", "ranges", "backport", "backport-cpp")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cor3ntin/rangesnext"
    license = "BSL-1.0"
    exports_sources = "patches/**"
    settings = "compiler"

    _compilers_minimum_version = {
        "gcc": "10",
        "Visual Studio": "19",
        "clang": "13"
    }
    _source_subfolder = "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "20")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version or tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("rangesnext requires C++20, which your compiler does not fully support.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        self._patch_sources()

        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def _patch_sources(self):
        for patchdata in self.conan_data["patches"][self.version]:
            tools.patch(**patchdata)
