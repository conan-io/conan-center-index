import os
from conan import ConanFile
from conan.tools import files
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.build import check_min_cppstd

required_conan_version = ">=1.53.0"


class MqttCppConan(ConanFile):
    name = "redboltz-mqtt_cpp"
    description = "MQTT client/server for C++14 based on Boost.Asio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/redboltz/mqtt_cpp"
    topics = ("mqtt", "tls", "boost", "websocket", "asio")
    license = "BSL-1.0"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "cpp17": [True, False],
        "fPIC": [True, False],
        "with_static_boost": [True, False],
        "with_static_openssl": [True, False],
        "with_tls": [True, False],
        "with_websocket": [True, False],
        "mqtt_always_send_reason_code": [True, False],
        "utf8_string": [True, False],
    }
    default_options = {
        "cpp17":  False,
        "fPIC":  True,
        "with_static_boost":  False,
        "with_static_openssl":  False,
        "with_tls":  False,
        "with_websocket":  False,
        "mqtt_always_send_reason_code":  True,
        "utf8_string":  False,
    }

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.80.0")
        if self.options.with_tls or self.options.with_websocket:
            self.requires("openssl/1.1.1s")
            self.requires("zlib/1.2.13")

    def package_id(self):
        self.info.header_only()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
            if self.options.get_safe("cpp17"):
                check_min_cppstd(self, 17)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MQTT_BUILD_EXAMPLES"] = False
        tc.variables["MQTT_BUILD_TESTS"] = False
        tc.variables["MQTT_ALWAYS_SEND_REASON_CODE"] = self.options.mqtt_always_send_reason_code
        tc.variables["MQTT_USE_STATIC_BOOST"] = self.options.with_static_boost
        if self.options.with_static_boost:
            openssl = self.dependencies["boost"]
            openssl.shared = True
        tc.variables["MQTT_USE_STATIC_OPENSSL"] = self.options.with_static_openssl
        if self.options.with_static_openssl:
            openssl = self.dependencies["openssl"]
            openssl.shared = False
        tc.variables["MQTT_USE_TLS"] = self.options.with_tls
        tc.variables["MQTT_USE_WS"] = self.options.with_websocket
        if self.options.get_safe("cpp17"):
            tc.variables["MQTT_STD_VARIANT"] = True
            tc.variables["MQTT_STD_OPTIONAL"] = True
            tc.variables["MQTT_STD_STRING_VIEW"] = True
            tc.variables["MQTT_STD_ANY"] = True
            tc.variables["MQTT_STD_SHARED_PTR_ARRAY"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt",
                  dst="licenses", src=self.source_folder)
        self.copy(pattern="*.hpp", dst="include",
                  src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mqtt_cpp")
        self.cpp_info.set_property(
            "cmake_target_name", "mqtt_cpp_iface::mqtt_cpp_iface")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mqtt_cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mqtt_cpp"
        self.cpp_info.names["cmake_find_package"] = "mqtt_cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "mqtt_cpp"
