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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ArduinoJson", self._source_subfolder)

    def package(self):
        self.copy("*LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "src"))
