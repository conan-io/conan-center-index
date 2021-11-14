from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class MaddyConan(ConanFile):
    name = "maddy"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/progsource/maddy"
    description = "open-source, maddy is a C++ Markdown to HTML header-only parser library."
    topics = ("maddy", "markdown", "header-only")
    license = "MIT"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("maddy-{}".format(self.version), self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        self.copy(
            pattern="maddy/*.h", src=os.path.join(self.source_folder, self._source_subfolder, "include"), dst="include"
        )
