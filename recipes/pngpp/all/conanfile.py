from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class PngppConan(ConanFile):
    name = "pngpp"
    description = "A C++ wrapper for libpng library."
    license = "BSD-3-Clause"
    topics = ("png++", "png")
    homepage = "https://www.nongnu.org/pngpp"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("libpng/1.6.37")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst=os.path.join("include", "png++"), src=self._source_subfolder)
