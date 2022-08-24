from conans import ConanFile, tools
from conans.errors import  ConanInvalidConfiguration
import os


class GetoptForVisualStudio(ConanFile):
    name = "getopt-for-visual-studio"
    description = "GNU getopt for Visual Studio"
    topics = ("conan", "getopt", "cli", "command line", "options")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skandhurkat/Getopt-for-Visual-Studio"
    license = "MIT", "BSD-2-Clause"
    exports_sources = "patches/**"
    settings = "compiler"

    def configure(self):
        if self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("getopt-for-visual-studio is only supported for Visual Studio")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("Getopt-for-Visual-Studio-{}".format(os.path.splitext(os.path.basename(self.conan_data["sources"][self.version]["url"]))[0]), self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)

    @property
    def _license_text(self):
        content = tools.files.load(self, os.path.join(self._source_subfolder, "getopt.h"))
        return "\n".join(list(l.strip() for l in content[content.find("/**", 3):content.find("#pragma")].split("\n")))

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)
        self.copy("getopt.h", src=self._source_subfolder, dst="include")

    def package_id(self):
        self.info.header_only()
