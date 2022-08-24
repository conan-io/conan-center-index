import os

from conans import ConanFile, tools


required_conan_version = ">=1.32.0"


class BrigandConan(ConanFile):
    name = "brigand"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A light-weight, fully functional, instant-compile time meta-programming library."
    topics = ("meta-programming", "boost", "runtime", "header-only")
    homepage = "https://github.com/edouarda/brigand"
    license = "BSL-1.0"
    settings = "compiler"
    requires = "boost/1.75.0"
    no_copy_sources = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        include_path = os.path.join("include", "brigand")
        self.copy("*.hpp", dst=include_path, src=os.path.join(self._source_subfolder, include_path))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libbrigand"
