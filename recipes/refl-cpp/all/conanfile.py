from conans import ConanFile, tools, errors


class ReflCppConan(ConanFile):
    name = "refl-cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/veselink1/refl-cpp"
    description = "A modern compile-time reflection library for C++ with support for overloads, templates, attributes and proxies "
    topics = ("header", "header-only", "reflection", "modern", "metaprogramming")
    no_copy_source = True
    settings =  "compiler"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def package(self):
        include_folder = self._source_subfolder
        self.copy(pattern="*.hpp", dst="include", src=include_folder)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "8",
            "clang": "8",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise errors.ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
