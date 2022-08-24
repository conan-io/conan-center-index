from conan import ConanFile, tools
from conans import errors

required_conan_version = ">=1.33.0"

class ImmerConan(ConanFile):
    name = "immer"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/arximboldi/immer"
    description = "Postmodern immutable and persistent data structures for C++---value semantics at scale"
    topics = ("header", "header-only", "persistent", "modern", "immutable",
              "data structures", "functional", "value semantics", "postmodern",
              "rrb-tree")
    no_copy_source = True
    settings =  "compiler"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True,
                  destination=self._source_subfolder)

    def package(self):
        include_folder = self._source_subfolder
        self.copy(pattern="*.hpp", dst="include", src=include_folder)
        self.copy(pattern="LICENSE", dst="licenses", src=include_folder)

    def package_id(self):
        self.info.header_only()

    @property
    def _minimum_compilers_version(self):
        # Reference: https://en.cppreference.com/w/cpp/compiler_support/14
        return {
            "apple-clang": "5.1",
            "clang": "3.4",
            "gcc": "6",
            "intel": "17",
            "sun-cc": "5.15",
            "Visual Studio": "15"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.scm.Version(self.settings.compiler.version) < min_version:
                raise errors.ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
