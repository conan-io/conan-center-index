from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class LAConan(ConanFile):
    name = "linear_algebra"
    homepage = "https://github.com/BobSteagall/wg21"
    description = "Production-quality reference implementation of P1385: A proposal to add linear algebra support to the C++ standard library"
    topics = ("linear-algebra", "multi-dimensional", "maths")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "11"
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} "
                             "compiler support.".format(
                                 self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()