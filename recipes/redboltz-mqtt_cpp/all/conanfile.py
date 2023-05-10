from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class MqttCppConan(ConanFile):
    name = "redboltz-mqtt_cpp"
    description = "MQTT client/server for C++14 based on Boost.Asio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/redboltz/mqtt_cpp"
    topics = ("mqtt", "mqttv5", "tls", "boost", "websocket", "asio")
    license = "BSL-1.0"
    no_copy_source = True
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_std_containers": [True, False],
        "with_tls": [True, False],
        "use_logs": [True, False],
        "use_websocket": [True, False],
        "with_tuple_any_workaround": [True, False],
        "mqtt_always_send_reason_code": [True, False],
    }
    default_options = {
        "enable_std_containers":  False,
        "with_tls":  False,
        "use_websocket":  False,
        "use_logs": True,
        "with_tuple_any_workaround": False
        "mqtt_always_send_reason_code":  True,
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _min_cppstd(self):
        if self.options.enable_std_containers:
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
                "clang": "3.4",
                "apple-clang": "5.1"
            },
        }[self._min_cppstd]


    def requirements(self):
        self.requires("boost/1.81.0")
        if self.options.with_tls:
            self.requires("openssl/[>=1.1 <4]")
            self.requires("zlib/1.2.13")

    def package_id(self):
        self.info.settings.clear() # We need to keep option since they change the binary

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        min_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires a compiler that supports at least C++{self._min_cppstd}")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MQTT_BUILD_EXAMPLES"] = False
        tc.variables["MQTT_BUILD_TESTS"] = False
        tc.variables["MQTT_ALWAYS_SEND_REASON_CODE"] = self.options.mqtt_always_send_reason_code
        tc.variables["MQTT_USE_STATIC_BOOST"] = not self.dependencies["boost"].options.get_safe("shared")
        if self.options.with_tls:
            tc.variables["MQTT_USE_STATIC_OPENSSL"] = not self.dependencies["openssl"].options.get_safe("shared")
        tc.variables["MQTT_USE_TLS"] = self.options.with_tls
        tc.variables["MQTT_USE_WS"] = self.options.use_websocket
        if self.options.enable_std_containers:
            tc.variables["MQTT_STD_VARIANT"] = True
            tc.variables["MQTT_STD_OPTIONAL"] = True
            tc.variables["MQTT_STD_STRING_VIEW"] = True
            tc.variables["MQTT_STD_ANY"] = True
            tc.variables["MQTT_STD_SHARED_PTR_ARRAY"] = True
        tc.variables["MQTT_USE_LOG"] = self.options.use_logs
        tc.variables["MQTT_DISABLE_LIBSTDCXX_TUPLE_ANY_WORKAROUND"] = self.options.with_tuple_any_workaround
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def package(self):
        copy(self, pattern="LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mqtt_cpp_iface")
        self.cpp_info.set_property("cmake_target_name", "mqtt_cpp_iface::mqtt_cpp_iface")

        if self.options.mqtt_always_send_reason_code:
            self.cpp_info.defines.append("MQTT_ALWAYS_SEND_REASON_CODE")
        if self.options.with_tls:
            self.cpp_info.defines.append("MQTT_USE_TLS")
        if self.options.use_websocket:
            self.cpp_info.defines.append("MQTT_USE_WS")
        if self.options.use_logs:
            self.cpp_info.defines.append("MQTT_USE_LOG")
        if self.options.enable_std_containers:
            self.cpp_info.defines.append("MQTT_STD_VARIANT")
            self.cpp_info.defines.append("MQTT_STD_OPTIONAL")
            self.cpp_info.defines.append("MQTT_STD_STRING_VIEW")
            self.cpp_info.defines.append("MQTT_STD_ANY")
            self.cpp_info.defines.append("MQTT_STD_SHARED_PTR_ARRAY")
        if self.options.with_tuple_any_workaround:
            self.cpp_info.defines.append("MQTT_DISABLE_LIBSTDCXX_TUPLE_ANY_WORKAROUND")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mqtt_cpp_iface"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mqtt_cpp_iface"
        self.cpp_info.names["cmake_find_package"] = "mqtt_cpp_iface"
        self.cpp_info.names["cmake_find_package_multi"] = "mqtt_cpp_iface"
