import os

from conans import ConanFile, tools
import glob


class InfluxDBCppConan(ConanFile):
    name = "influxdb-cpp"
    license = "MIT"
    homepage = "https://github.com/orca-zhang/influxdb-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ client for InfluxDB."
    topics = ("single-header-lib", "influxdb")
    settings = "os"
    exports_sources = ["patches/**"]
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("influxdb-cpp-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

    def package(self):
        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)
        self.copy('influxdb.hpp', dst='include', src=self._source_subfolder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.defines = ["NOMINMAX"]
            self.cpp_info.system_libs = ["ws2_32"]

    def package_id(self):
        self.info.header_only()
