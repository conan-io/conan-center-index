from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"

class StatsLibConan(ConanFile):
    name = "statslib"
    description = "A C++ header-only library of statistical distribution functions."
    topics = ("statistics", "constexpr", "probability", "stats")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kthohr.com/statslib.html"
    license = "Apache-2.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("gcem/1.14.1")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
