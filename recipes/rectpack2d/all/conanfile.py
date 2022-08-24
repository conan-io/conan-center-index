from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class Rectpack2dConan(ConanFile):
    name = "rectpack2d"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/TeamHypersomnia/rectpack2D"
    description = "C++17 rectangle packing library"
    topics = ("header-only", "rectpack2d", "graphical", "cpp17")
    license = "MIT"
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.scm.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*.h", dst=os.path.join("include", "rectpack2d"),
                  src=os.path.join(self._source_subfolder, "src"))

    def package_id(self):
        self.info.header_only()

