import os
from conans import ConanFile, CMake, tools


class DateConan(ConanFile):
    name = "date"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HowardHinnant/date"
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    topics = ("date", "datetime", "timezone", "calendar", "time", "iana-database")
    license = "MIT"
    exports_sources = ["patches/*"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        cmake.definitions["USE_SYSTEM_TZ_DB"] = True
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        
    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()