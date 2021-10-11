import os

from conans import ConanFile, tools


class EmbeddedTemplateLibraryConan(ConanFile):
    name = "embedded-template-library"
    license = "MIT"
    author = "John Wellbelove <john.wellbelove@etlcpp.com>"
    url = "https://github.com/ETLCPP/etl"
    description = "A C++ template library for embedded applications"
    topics = ("C++", "embedded", "template", "container", "utility", "framework", "messaging")
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        self.copy("LICENSE", "licenses")
        self.copy(os.path.join("include", "etl", "*.h"))

    def package_id(self):
        self.info.header_only()
