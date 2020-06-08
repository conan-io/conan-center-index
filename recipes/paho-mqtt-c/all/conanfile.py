import os
from conans import CMake, ConanFile, tools

class PahoMqttcConan(ConanFile):
    name = "paho-mqtt-c"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.c"
    topics = ("MQTT", "IoT", "eclipse", "SSL", "paho", "C")
    license = "EPL-2.0"
    description = """Eclipse Paho MQTT C client library for Linux, Windows and MacOS"""
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "ssl": [True, False],
               "asynchronous": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "ssl": False,
                       "asynchronous": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1g")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PAHO_ENABLE_TESTING"] = False
        self._cmake.definitions["PAHO_BUILD_DOCUMENTATION"] = False
        self._cmake.definitions["PAHO_BUILD_SAMPLES"] = False
        self._cmake.definitions["PAHO_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["PAHO_BUILD_ASYNC"] = self.options.asynchronous
        self._cmake.definitions["PAHO_WITH_SSL"] = self.options.ssl
        if self.options.ssl:
            self._cmake.definitions["OPENSSL_SEARCH_PATH"] = self.deps_cpp_info["openssl"].rootpath
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
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.system_libs.append("ws2_32")
                if self.settings.compiler == "gcc":
                    self.cpp_info.system_libs.extend(
                        ["wsock32", "uuid", "crypt32", "rpcrt4"])
        else:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.extend(["c", "dl", "pthread"])
            elif self.settings.os == "FreeBSD":
                self.cpp_info.system_libs.extend(["compat", "pthread"])
            elif self.settings.os == "Android":
                self.cpp_info.system_libs.extend(["c"])
            else:
                self.cpp_info.system_libs.extend(["c", "pthread"])
        self.cpp_info.names["cmake_find_package"] = "PahoMqttC"
        self.cpp_info.names["cmake_find_package_multi"] = "PahoMqttC"

