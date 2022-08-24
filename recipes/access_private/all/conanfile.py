import os

from conans import ConanFile, tools


class AccessPrivateConan(ConanFile):
    name = "access_private"
    description = "Access private members and statics of a C++ class"
    license = ["MIT"]
    topics = ("conan", "access", "private", "header-only")
    homepage = "https://github.com/martong/access_private"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = "access_private-" + \
            os.path.splitext(os.path.basename(url))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE",
                  dst="licenses",
                  src=self._source_subfolder)
        self.copy("access_private.hpp",
                  dst=os.path.join("include", "access_private"),
                  src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
