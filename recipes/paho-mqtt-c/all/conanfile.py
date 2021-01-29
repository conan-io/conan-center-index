import os
import glob
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class PahoMqttcConan(ConanFile):
    name = "paho-mqtt-c"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.c"
    topics = ("MQTT", "IoT", "eclipse", "SSL", "paho", "C")
    license = "EPL-2.0"
    description = "Eclipse Paho MQTT C client library for Linux, Windows and MacOS"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "ssl": [True, False],
               "samples": [True, False],
               "asynchronous": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "ssl": True,
                       "asynchronous" : True,
                       "samples": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # There is uncertainty if static linking before 1.3.4 worked.
        # If you need it, tweak here, on Linux and OSX you might have success.
        if tools.Version(self.version) < "1.3.4":
            self.options.shared = True

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared == False and self.settings.os == "Windows" and tools.Version(self.version) < "1.3.4":
            raise ConanInvalidConfiguration("Static linking in Windows did not work before version 1.3.4")

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1i")

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
        self._cmake.definitions["PAHO_ENABLE_CPACK"] = False
        self._cmake.definitions["PAHO_BUILD_DEB_PACKAGE"] = False
        self._cmake.definitions["PAHO_BUILD_ASYNC"] = self.options.asynchronous
        self._cmake.definitions["PAHO_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["PAHO_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["PAHO_BUILD_SAMPLES"] = self.options.samples
        self._cmake.definitions["PAHO_WITH_SSL"] = self.options.ssl
        if self.options.ssl:
            self._cmake.definitions["OPENSSL_SEARCH_PATH"] = self.deps_cpp_info["openssl"].rootpath
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()
        # cmake.build(target=self._cmake_target)

    def package(self):
        self.copy("edl-v10", src=self._source_subfolder, dst="licenses")
        if self.version in ['1.3.0', '1.3.1']:
            eplfile = "epl-v10"
        else:
            eplfile = "epl-v20" # EPL changed to V2
        self.copy(eplfile, src=self._source_subfolder, dst="licenses")
        self.copy("notice.html", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        # Remove the extra version that do not match the options
        for lib_pattern in ["*paho-mqtt3as*", "*paho-mqtt3cs*", "*paho-mqtt3c.*", "*paho-mqtt3a.*",
                            "*paho-mqtt3as-static*", "*paho-mqtt3cs-static*", "*paho-mqtt3c-static*", "*paho-mqtt3a-static*"]:
            if not self._lib_target in lib_pattern:
                for lib_file in glob.glob(os.path.join(self.package_folder, "lib", lib_pattern)):
                    os.remove(lib_file)

    def package_info(self):
        if tools.Version(self.version) < "1.3.4" and self.options.shared:
            self.output.warn("This should be impossible")
        self.cpp_info.names["cmake_find_package"] = "eclipse-paho-mqtt-c"
        self.cpp_info.names["cmake_find_package_multi"] = "eclipse-paho-mqtt-c"
        self.cpp_info.components["_paho-mqtt-c"].names["cmake_find_package"] = self._cmake_target
        self.cpp_info.components["_paho-mqtt-c"].names["cmake_find_package_multi"] = self._cmake_target
        self.cpp_info.components["_paho-mqtt-c"].libs = [self._lib_target]
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.components["_paho-mqtt-c"].system_libs.append("ws2_32")
                if self.settings.compiler == "gcc":
                    self.cpp_info.components["_paho-mqtt-c"].system_libs.extend(
                        ["wsock32", "uuid", "crypt32", "rpcrt4"])
        else:
            if self.settings.os == "Linux":
                self.cpp_info.components["_paho-mqtt-c"].system_libs.extend(["c", "dl", "pthread"])
            elif self.settings.os == "FreeBSD":
                self.cpp_info.components["_paho-mqtt-c"].system_libs.extend(["compat", "pthread"])
            elif self.settings.os == "Android":
                self.cpp_info.components["_paho-mqtt-c"].system_libs.extend(["c"])
            else:
                self.cpp_info.components["_paho-mqtt-c"].system_libs.extend(["c", "pthread"])
        if self.options.ssl:
            self.cpp_info.components["_paho-mqtt-c"].requires = ["openssl::openssl"]

    @property
    def _cmake_target(self):
        target = "paho-mqtt3"
        target += "a" if self.options.asynchronous else "c"
        if self.options.ssl:
            target += "s"
        if not self.options.shared:
            target += "-static"
        return target

    @property
    def _lib_target(self):
        target = "paho-mqtt3"
        target += "a" if self.options.asynchronous else "c"
        if self.options.ssl:
            target += "s"
        if not self.options.shared:
            # https://github.com/eclipse/paho.mqtt.c/blob/317fb008e1541838d1c29076d2bc5c3e4b6c4f53/src/CMakeLists.txt#L154
            if tools.Version(self.version) < "1.3.2" or self.settings.os == "Windows":
                target += "-static"
        return target
