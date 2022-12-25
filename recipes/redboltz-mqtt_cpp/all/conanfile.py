import os
from conan import ConanFile
from conan.tools import files
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class MqttCppConan(ConanFile):
    name = "redboltz-mqtt_cpp"
    description = "MQTT client/server for C++14 based on Boost.Asio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/redboltz/mqtt_cpp"
    topics = ("mqtt", "mqttv5", "tls", "boost", "websocket", "asio")
    license = "BSL-1.0"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "cpp17": [True, False],
        "with_tls": [True, False],
        "with_websocket": [True, False],
        "mqtt_always_send_reason_code": [True, False],
        "utf8_string": [True, False],
        "with_logs": [True, False],
        "with_tuple_any_workaround": [True, False],
    }
    default_options = {
        "cpp17":  False,
        "with_tls":  False,
        "with_websocket":  False,
        "mqtt_always_send_reason_code":  True,
        "utf8_string":  True,
        "with_logs": True,
        "with_tuple_any_workaround": False
    }

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    @property
    def _min_cppstd(self):
        if self.options.get_safe("cpp17"):
            return "17"
        return "14"

    @property
    def _minimum_compiler_version(self):
        return {
            "17": {
                "Visual Studio": "16",
                "gcc": "7.3",
                "clang": "6.0",
                "apple-clang": "10.0"
            },
            "14": {
                "Visual Studio": "15",
                "gcc": "6",
                "clang": "5",
                "apple-clang": "8.0"
            },
        }[self._min_cppstd]


    def requirements(self):
        self.requires("boost/1.80.0")
        if self.options.with_tls:
            self.requires("openssl/1.1.1s")
            self.requires("zlib/1.2.13")

    def package_id(self):
        self.info.header_only()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        min_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(
                    self.name, self._min_cppstd,
                )
            )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MQTT_BUILD_EXAMPLES"] = False
        tc.variables["MQTT_BUILD_TESTS"] = False
        tc.variables["MQTT_ALWAYS_SEND_REASON_CODE"] = self.options.mqtt_always_send_reason_code
        tc.variables["MQTT_USE_STATIC_BOOST"] = not self.dependencies.direct_host["boost"].options.get_safe(
            "shared")
        if self.options.with_tls:
            tc.variables["MQTT_USE_STATIC_OPENSSL"] = not self.dependencies["openssl"].options.get_safe(
                "shared")
        tc.variables["MQTT_USE_TLS"] = self.options.with_tls
        tc.variables["MQTT_USE_WS"] = self.options.with_websocket
        if self.options.get_safe("cpp17"):
            tc.variables["MQTT_STD_VARIANT"] = True
            tc.variables["MQTT_STD_OPTIONAL"] = True
            tc.variables["MQTT_STD_STRING_VIEW"] = True
            tc.variables["MQTT_STD_ANY"] = True
            tc.variables["MQTT_STD_SHARED_PTR_ARRAY"] = True
        tc.variables["MQTT_USE_LOG"] = self.options.with_logs
        tc.variables["MQTT_DISABLE_LIBSTDCXX_TUPLE_ANY_WORKAROUND"] = self.options.with_tuple_any_workaround
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt",
                  dst="licenses", src=self.source_folder)
        self.copy(pattern="*.hpp", dst="include",
                  src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        if self.options.mqtt_always_send_reason_code:
            self.cpp_info.defines.append("MQTT_ALWAYS_SEND_REASON_CODE")
        if self.options.with_tls:
            self.cpp_info.defines.append("MQTT_USE_TLS")
        if self.options.with_websocket:
            self.cpp_info.defines.append("MQTT_USE_WS")
        if self.options.with_logs:
            self.cpp_info.defines.append("MQTT_USE_LOG")
        if self.options.cpp17:
            self.cpp_info.defines.append("MQTT_STD_VARIANT")
            self.cpp_info.defines.append("MQTT_STD_OPTIONAL")
            self.cpp_info.defines.append("MQTT_STD_STRING_VIEW")
            self.cpp_info.defines.append("MQTT_STD_ANY")
            self.cpp_info.defines.append("MQTT_STD_SHARED_PTR_ARRAY")
        if self.options.with_tuple_any_workaround:
            self.cpp_info.defines.append(
                "MQTT_DISABLE_LIBSTDCXX_TUPLE_ANY_WORKAROUND")

        self.cpp_info.set_property("cmake_file_name", "mqtt_cpp_iface")
        self.cpp_info.set_property("cmake_file_name", "mqtt_cpp_iface")
        self.cpp_info.set_property(
            "cmake_target_name", "mqtt_cpp_iface::mqtt_cpp_iface")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mqtt_cpp_iface"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mqtt_cpp_iface"
        self.cpp_info.names["cmake_find_package"] = "mqtt_cpp_iface"
        self.cpp_info.names["cmake_find_package_multi"] = "mqtt_cpp_iface"
