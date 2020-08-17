from conans import ConanFile, tools
import os


class ArduinojsonConan(ConanFile):
    name = "arduinojson"
    license = "The MIT License (MIT)"
    description = "C++ JSON library for IoT. Simple and efficient."
    homepage = "https://github.com/bblanchon/ArduinoJson"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("json", "arduino", "iot", "embedded", "esp8266")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ArduinoJson", self._source_subfolder)

    def package(self):
        self.copy("*LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src"))
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "src"))

    def package_info(self):
        # TODO: CMake imported target shouldn't be namespaced
        self.cpp_info.names["cmake_find_package"] = "ArduinoJson"
        self.cpp_info.names["cmake_find_package_multi"] = "ArduinoJson"
