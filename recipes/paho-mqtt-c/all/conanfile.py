from conans import CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PahoMqttcConan(ConanFile):
    name = "paho-mqtt-c"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.c"
    topics = ("mqtt", "iot", "eclipse", "ssl", "tls", "paho", "c")
    license = "EPL-2.0"
    description = "Eclipse Paho MQTT C client library for Linux, Windows and MacOS"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
        "asynchronous": [True, False],
        "samples": [True, False, "deprecated"],
        "high_performance": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": True,
        "asynchronous": True,
        "samples": "deprecated",
        "high_performance": False
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_high_performance_option(self):
        return tools.Version(self.version) >= "1.3.2"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not self._has_high_performance_option:
            del self.options.high_performance

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

        if self.options.samples != "deprecated":
            self.output.warn("samples option is deprecated and they are no longer provided in the package.")

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        if not self.options.shared and tools.Version(self.version) < "1.3.4":
            raise ConanInvalidConfiguration("{}/{} does not support static linking".format(self.name, self.version))

    def package_id(self):
        del self.info.options.samples

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
        self._cmake.definitions["PAHO_BUILD_SAMPLES"] = False
        self._cmake.definitions["PAHO_WITH_SSL"] = self.options.ssl
        if self.options.ssl:
            self._cmake.definitions["OPENSSL_SEARCH_PATH"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
        if self._has_high_performance_option:
            self._cmake.definitions["PAHO_HIGH_PERFORMANCE"] = self.options.high_performance
        self._cmake.configure()
        return self._cmake

    def _patch_source(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "SET(CMAKE_MODULE_PATH \"${CMAKE_SOURCE_DIR}/cmake/modules\")",
                              "LIST(APPEND CMAKE_MODULE_PATH \"${CMAKE_SOURCE_DIR}/cmake/modules\")")
        if not self.options.get_safe("fPIC", True):
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"), "POSITION_INDEPENDENT_CODE ON", "")

    def build(self):
        self._patch_source()
        cmake = self._configure_cmake()
        cmake.build(target=self._cmake_target)

    def package(self):
        self.copy("edl-v10", src=self._source_subfolder, dst="licenses")
        self.copy(self._epl_file, src=self._source_subfolder, dst="licenses")
        self.copy("notice.html", src=self._source_subfolder, dst="licenses")
        # Manually copy since the CMake installs everything
        self.copy(pattern="MQTT*.h", src=os.path.join(self._source_subfolder, "src"), dst="include")
        self.copy(os.path.join("lib", "*{}.*".format(self._lib_target)), dst="lib", keep_path=False)
        self.copy(os.path.join("bin", "*{}.*".format(self._lib_target)), dst="bin", keep_path=False)
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
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
    def _epl_file(self):
        return "epl-v10" if self.version in ['1.3.0', '1.3.1'] else "epl-v20" # EPL changed to V2

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
