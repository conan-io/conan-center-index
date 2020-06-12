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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ArduinoJson", "sources")

    def package(self):
        self.copy("*LICENSE*", dst="licenses", src="sources")
        self.copy("*.h", dst="include", src="sources")
        self.copy("*.hpp", dst="include", src="sources")

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "src"))
