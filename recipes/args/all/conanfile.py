from conans import ConanFile, tools


class ArgsConan(ConanFile):
    name = "args"
    description = "A simple header-only C++ argument parser library."
    topics = ("conan", "args", "argument", "parsing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Taywee/args"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True,
                  destination=self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="license")
        self.copy("args.hxx", src=self._source_subfolder, dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append("include")
