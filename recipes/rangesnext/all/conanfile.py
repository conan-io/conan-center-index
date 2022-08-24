from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class RangesnextConan(ConanFile):
    name = "rangesnext"
    description = "ranges features for C++23 ported to C++20"
    topics = ("conan", "rangesnext", "ranges", "backport", "backport-cpp")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cor3ntin/rangesnext"
    license = "BSL-1.0"
    settings = "compiler"
    no_copy_source = True

    _compilers_minimum_version = {
        "gcc": "10",
        "Visual Studio": "19",
        "clang": "13"
    }
    _source_subfolder = "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "20")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version or tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("rangesnext requires C++20, which your compiler does not fully support.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)
