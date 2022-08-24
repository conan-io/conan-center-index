import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class IndicatorsConan(ConanFile):
    name = "indicators"
    homepage = "https://github.com/p-ranav/indicators"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Activity Indicators for Modern C++"
    license = "MIT"
    settings = "compiler", "os"
    topics = ("conan", "indicators", "activity", "indicator", "loading", "spinner", "animation", "progress")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 11)

        if tools.scm.Version(self.version) < "2.0" and self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                "indicators < 2.0 can't be used by {0} {1}".format(
                    self.settings.compiler,
                    self.settings.compiler.version
                )
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
