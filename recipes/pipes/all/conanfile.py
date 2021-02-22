from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

class PipesConan(ConanFile):
    name = "pipes"
    description = "Pipelines for expressive code on collections in C++"
    license = "MIT"
    topics = ("pipes", "functional-programming")
    homepage = "https://github.com/joboccara/pipes"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def package_id(self):
        self.info.header_only()
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pipes-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"), keep_path=True)
