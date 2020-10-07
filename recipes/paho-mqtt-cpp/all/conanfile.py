import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class PahoMqttCppConan(ConanFile):
    name = "paho-mqtt-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.cpp"
    topics = ("MQTT", "IoT", "eclipse", "SSL", "paho", "Cpp")
    license = "EPL-1.0"
    description = """The open-source client implementations of MQTT and MQTT-SN"""
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "ssl": [True, False],
               }
    default_options = {"shared": False,
                       "fPIC": True,
                       "ssl": True
                       }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "Paho cpp can not be built as shared on Windows.")

        self.options["paho-mqtt-c"].shared = self.options.shared
        self.options["paho-mqtt-c"].ssl = self.options.ssl


    def requirements(self):
        self.requires("paho-mqtt-c/1.3.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PAHO_BUILD_DOCUMENTATION"] = False
        self._cmake.definitions["PAHO_BUILD_SAMPLES"] = False
        self._cmake.definitions["PAHO_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["PAHO_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["PAHO_WITH_SSL"] = self.options.ssl
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("edl-v10", src=self._source_subfolder, dst="licenses")
        self.copy("epl-v10", src=self._source_subfolder, dst="licenses")
        self.copy("notice.html", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PahoMqttCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "PahoMqttCpp"
        target = "paho-mqttpp3" if self.options.shared else "paho-mqttpp3-static"
        self.cpp_info.components["paho-mqttpp"].names["cmake_find_package"] = target
        self.cpp_info.components["paho-mqttpp"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["paho-mqttpp"].requires = ["paho-mqtt-c::paho-mqtt-c"]
        if self.settings.os == "Windows":
            self.cpp_info.components["paho-mqttpp"].libs = [target]
        else:
            self.cpp_info.components["paho-mqttpp"].libs = ["paho-mqttpp3"]
