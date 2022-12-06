from conan import ConanFile
from conan.tools import files
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"


class MqttCppConan(ConanFile):
    name = "redboltz-mqtt_cpp"
    description = "MQTT client/server for C++14 based on Boost.Asio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/redboltz/mqtt_cpp"
    topics = ("mqtt", "tls", "boost", "websocket", "asio")
    license = "BSL-1.0"
    # exports_sources = "include/*"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

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
        "with_tls":  True,
        "with_websocket":  False,
        "mqtt_always_send_reason_code":  False,
        "utf8_string":  False,
    }
    exports_sources =  "CMakeLists.txt"

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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MQTT_BUILD_EXAMPLES"] = False
        tc.variables["MQTT_BUILD_TESTS"] = False
        tc.variables["MQTT_ALWAYS_SEND_REASON_CODE"] = self.options.mqtt_always_send_reason_code
        tc.variables["MQTT_USE_STATIC_BOOST"] = self.options.with_static_boost
        tc.variables["MQTT_USE_STATIC_OPENSSL"] = self.options.with_static_openssl
        tc.variables["MQTT_USE_TLS"] = self.options.with_tls
        tc.variables["MQTT_USE_WS"] = self.options.with_websocket
        if self.options.get_safe("cpp17"):
            self._cmake.definitions["MQTT_STD_VARIANT"] = True
            self._cmake.definitions["MQTT_STD_OPTIONAL"] = True
            self._cmake.definitions["MQTT_STD_STRING_VIEW"] = True
            self._cmake.definitions["MQTT_STD_ANY"] = True
            self._cmake.definitions["MQTT_STD_SHARED_PTR_ARRAY"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    # def source(self):
    #     tools.get(**self.conan_data["sources"][self.version],
    #               destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        # cmake = CMake(self)
        # cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # files.rmdir(self, os.path.join(self.package_folder, "lib", "cpprestsdk"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mqtt_cpp")
        self.cpp_info.set_property("cmake_target_name", "mqtt_cpp::mqtt_cpp")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mqtt_cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mqtt_cpp"
        self.cpp_info.names["cmake_find_package"] = "mqtt_cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "mqtt_cpp"

        # # cpprestsdk_boost_internal
        # self.cpp_info.components["cpprestsdk_boost_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_boost_internal")
        # self.cpp_info.components["cpprestsdk_boost_internal"].includedirs = []
        # self.cpp_info.components["cpprestsdk_boost_internal"].requires = ["boost::boost"]
        # # cpprestsdk_openssl_internal
        # self.cpp_info.components["cpprestsdk_openssl_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_openssl_internal")
        # self.cpp_info.components["cpprestsdk_openssl_internal"].includedirs = []
        # self.cpp_info.components["cpprestsdk_openssl_internal"].requires = ["openssl::openssl"]
        # # cpprest
        # self.cpp_info.components["cpprest"].set_property("cmake_target_name", "cpprestsdk::cpprest")
        # self.cpp_info.components["cpprest"].libs = files.collect_libs(self)
        # self.cpp_info.components["cpprest"].requires = ["cpprestsdk_boost_internal", "cpprestsdk_openssl_internal"]
        # if self.settings.os == "Linux":
        #     self.cpp_info.components["cpprest"].system_libs.append("pthread")
        # elif self.settings.os == "Windows":
        #     if self.options.get_safe("http_client_impl") == "winhttp":
        #         self.cpp_info.components["cpprest"].system_libs.append("winhttp")
        #     if self.options.get_safe("http_listener_impl") == "httpsys":
        #         self.cpp_info.components["cpprest"].system_libs.append("httpapi")
        #     self.cpp_info.components["cpprest"].system_libs.append("bcrypt")
        #     if self.options.get_safe("pplx_impl") == "winpplx":
        #         self.cpp_info.components["cpprest"].defines.append("CPPREST_FORCE_PPLX=1")
        #     if self.options.get_safe("http_client_impl") == "asio":
        #         self.cpp_info.components["cpprest"].defines.append("CPPREST_FORCE_HTTP_CLIENT_ASIO")
        #     if self.options.get_safe("http_listener_impl") == "asio":
        #         self.cpp_info.components["cpprest"].defines.append("CPPREST_FORCE_HTTP_LISTENER_ASIO")
        # elif self.settings.os == "Macos":
        #     self.cpp_info.components["cpprest"].frameworks.extend(["CoreFoundation", "Security"])
        # if not self.options.shared:
        #     self.cpp_info.components["cpprest"].defines.extend(["_NO_ASYNCRTIMP", "_NO_PPLXIMP"])
        # # cpprestsdk_zlib_internal
        # if self.options.with_compression:
        #     self.cpp_info.components["cpprestsdk_zlib_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_zlib_internal")
        #     self.cpp_info.components["cpprestsdk_zlib_internal"].includedirs = []
        #     self.cpp_info.components["cpprestsdk_zlib_internal"].requires = ["zlib::zlib"]
        #     self.cpp_info.components["cpprest"].requires.append("cpprestsdk_zlib_internal")
        # # cpprestsdk_websocketpp_internal
        # if self.options.with_websockets:
        #     self.cpp_info.components["cpprestsdk_websocketpp_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_websocketpp_internal")
        #     self.cpp_info.components["cpprestsdk_websocketpp_internal"].includedirs = []
        #     self.cpp_info.components["cpprestsdk_websocketpp_internal"].requires = ["websocketpp::websocketpp"]
        #     self.cpp_info.components["cpprest"].requires.append("cpprestsdk_websocketpp_internal")
