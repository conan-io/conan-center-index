from conans import ConanFile, tools
import os

class NoWideConan(ConanFile):
    name = "zippy"
    description = "A simple C++ wrapper around the \"miniz\" zip library "
    topics = ("wrapper", "compression", "zip")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/troldal/Zippy"
    license = "MIT"
    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("miniz/2.2.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "library"))

    def package_id(self):
        self.info.header_only()
