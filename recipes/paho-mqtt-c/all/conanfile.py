import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class PahoMqttcConan(ConanFile):
    name = "paho-mqtt-c"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.c"
    topics = ("MQTT", "IoT", "eclipse", "SSL", "paho", "C")
    license = "EPL-1.0"
    description = """The Eclipse Paho project provides open-source client implementations of MQTT
    and MQTT-SN messaging protocols aimed at new, existing, and emerging applications for the Internet
    of Things (IoT)"""
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "SSL": [True, False],
               "asynchronous": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "SSL": False,
                       "asynchronous": True}

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
        if self.options.SSL:
            self.requires("OpenSSL/1.1.1d")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PAHO_ENABLE_TESTING"] = False
        cmake.definitions["PAHO_BUILD_DOCUMENTATION"] = False
        cmake.definitions["PAHO_BUILD_SAMPLES"] = False
        cmake.definitions["PAHO_BUILD_STATIC"] = not self.options.shared
        cmake.definitions["PAHO_WITH_SSL"] = self.options.SSL
        cmake.definitions["PAHO_BUILD_ASYNC"] = self.options.asynchronous
        cmake.configure()
        return cmake

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
                self.cpp_info.libs.append("ws2_32")
                if self.settings.compiler == "gcc":
                    self.cpp_info.libs.extend(
                        ["wsock32", "uuid", "crypt32", "rpcrt4"])
        else:
            if self.settings.os == "Linux":
                self.cpp_info.libs.extend(["c", "dl", "pthread"])
            elif self.settings.os == "FreeBSD":
                self.cpp_info.libs.extend(["compat", "pthread"])
            else:
                self.cpp_info.libs.extend(["c", "pthread"])
