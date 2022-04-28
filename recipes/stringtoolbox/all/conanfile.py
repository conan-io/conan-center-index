from conans import ConanFile, tools

required_conan_version = ">=1.33.0"

class DawHeaderLibrariesConan(ConanFile):
    name = "stringtoolbox"
    license = "MIT"
    description = "A simple header-only, single-file string toolbox library for C++."
    topics = ("string", "header-only",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chrberger/stringtoolbox"
    settings = "os", "arch", "compiler", "build_type",
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "11")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        self.copy("stringtoolbox.hpp", "include", self._source_subfolder)
