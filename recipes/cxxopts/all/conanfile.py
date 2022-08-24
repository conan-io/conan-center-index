import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class CxxOptsConan(ConanFile):
    name = "cxxopts"
    homepage = "https://github.com/jarro2783/cxxopts"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Lightweight C++ option parser library, supporting the standard GNU style syntax for options."
    license = "MIT"
    topics = ("option-parser", "positional-arguments ", "header-only")
    settings = "compiler"
    options = { "unicode": [True, False] }
    default_options = { "unicode": False }
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "gcc": "5",
            "clang": "3.9",
            "apple-clang": "8",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.scm.Version(self, self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    def requirements(self):
        if self.options.unicode:
            self.requires("icu/70.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("{}.hpp".format(self.name), dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.unicode:
            self.cpp_info.defines = ["CXXOPTS_USE_UNICODE"]
