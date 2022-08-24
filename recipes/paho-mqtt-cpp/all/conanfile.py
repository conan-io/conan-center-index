import os
from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


class PahoMqttCppConan(ConanFile):
    name = "paho-mqtt-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.cpp"
    topics = ("mqtt", "iot", "eclipse", "ssl", "paho", "cpp")
    license = "EPL-1.0"
    description = "The open-source client implementations of MQTT and MQTT-SN"
    exports_sources = ["CMakeLists.txt", "patches/**"]
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
        if self.options.shared:
            del self.options.fPIC

        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, minimal_cpp_standard)

        self.options["paho-mqtt-c"].shared = self.options.shared
        self.options["paho-mqtt-c"].ssl = self.options.ssl

    def validate(self):
        if self.options["paho-mqtt-c"].shared != self.options.shared:
            raise ConanInvalidConfiguration("{} requires paho-mqtt-c to have a matching 'shared' option.".format(self.name))
        if self.options["paho-mqtt-c"].ssl != self.options.ssl:
            raise ConanInvalidConfiguration("{} requires paho-mqtt-c to have a matching 'ssl' option.".format(self.name))

    def requirements(self):
        if tools.scm.Version(self, self.version) >= "1.2.0":
            self.requires("paho-mqtt-c/1.3.9")
        else:
            self.requires("paho-mqtt-c/1.3.1") # https://github.com/eclipse/paho.mqtt.cpp/releases/tag/v1.1

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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
        # See this conversation https://github.com/conan-io/conan-center-index/pull/4096#discussion_r556119143
        # Changed by https://github.com/eclipse/paho.mqtt.c/commit/f875768984574fede6065c8ede0a7eac890a6e09
        # and https://github.com/eclipse/paho.mqtt.c/commit/c116b725fff631180414a6e99701977715a4a690
        # FIXME: after https://github.com/conan-io/conan/pull/8053#pullrequestreview-541120387
        if tools.scm.Version(self, self.version) < "1.2.0" and tools.scm.Version(self, self.deps_cpp_info["paho-mqtt-c"].version) >= "1.3.2":
            raise ConanInvalidConfiguration("{}/{} requires paho-mqtt-c =< 1.3.1".format(self.name, self.version))

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("edl-v10", src=self._source_subfolder, dst="licenses")
        self.copy("epl-v10", src=self._source_subfolder, dst="licenses")
        self.copy("notice.html", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

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
