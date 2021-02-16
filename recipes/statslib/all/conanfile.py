from conans import ConanFile, tools
import os


class StatsLibConan(ConanFile):
    name = "statslib"
    description = "A C++ header-only library of statistical distribution functions."
    topics = ("conan", "statistics", "constexpr", "probability", "stats")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kthohr.com/statslib.html"
    license = "Apache-2.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("gcem/1.13.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("stats-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
