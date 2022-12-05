from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os
from conan.tools.files import apply_conandata_patches

required_conan_version = ">=1.52.0"

class MqttCPPConan(ConanFile):
    name = "redboltz-mqtt_cpp"
    description = "MQTT client/server for C++14 based on Boost.Asio"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/redboltz/mqtt_cpp"
    topics = ("mqtt", "boost", "asio")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    no_copy_source = True
    cpp_version = 14

    options = {"cpp17": [True, False],
               "static_boost": [True, False],
               "static_openssl": [True, False],
               "tls": [True, False],
               "websockets": [True, False],
               "mqtt_always_send_reason_code": [True, False],
               }
    default_options = {"c++17": False,
                       "static_boost": False,
                       "static_openssl": False,
                       "tls": False,
                       "websockets": False,
                       "mqtt_always_send_reason_code": False
                       }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.79.0")

    def package_id(self):
        self.info.header_only()

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if options.cpp17:
                self.cpp_version = 17
            tools.check_min_cppstd(self, self.cpp_version)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++{}, which your compiler does not support.".format(self.name, self.cpp_version))
        else:
            self.output.warn("{} requires C++{}. Your compiler is unknown. Assuming it supports C++{}.".format(self.name, self.cpp_version, self.cpp_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MQTT_BUILD_EXAMPLES"] = False
        self._cmake.definitions["MQTT_BUILD_TESTS"] = False
        self._cmake.definitions["MQTT_ALWAYS_SEND_REASON_CODE"] = self.options.mqtt_always_send_reason_code
        self._cmake.definitions["MQTT_USE_STATIC_BOOST"] = self.options.static_boost
        self._cmake.definitions["MQTT_USE_STATIC_OPENSSL"] = self.options.static_openssl

        self._cmake.definitions["MQTT_USE_TLS"] = self.options.tls
        self._cmake.definitions["MQTT_USE_WS"] = self.options.websockets
        if self.cpp_version == 17:
            self._cmake.definitions["MQTT_STD_VARIANT"] = True
            self._cmake.definitions["MQTT_STD_OPTIONAL"] = True
            self._cmake.definitions["MQTT_STD_STRING_VIEW"] = True
            self._cmake.definitions["MQTT_STD_ANY"] = True
            self._cmake.definitions["MQTT_STD_SHARED_PTR_ARRAY"] = True

        self._cmake.configure()
        return self._cmake

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MQTT_BUILD_EXAMPLES"] = False
        tc.variables["MQTT_BUILD_TESTS"] = False
        tc.variables["MQTT_ALWAYS_SEND_REASON_CODE"] = self.options.mqtt_always_send_reason_code
        tc.variables["MQTT_USE_STATIC_BOOST"] = self.options.static_boost
        tc.variables["MQTT_USE_STATIC_OPENSSL"] = self.options.static_openssl

        tc.variables["MQTT_USE_TLS"] = self.options.tls
        tc.variables["MQTT_USE_WS"] = self.options.websockets
        if self.cpp_version == 17:
            tc.variables["MQTT_STD_VARIANT"] = True
            tc.variables["MQTT_STD_OPTIONAL"] = True
            tc.variables["MQTT_STD_STRING_VIEW"] = True
            tc.variables["MQTT_STD_ANY"] = True
            tc.variables["MQTT_STD_SHARED_PTR_ARRAY"] = True

        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mqtt_cpp_iface")
        self.cpp_info.set_property("cmake_target_name", "mqtt_cpp_iface::mqtt_cpp_iface")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mqtt_cpp_iface"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mqtt_cpp_iface"
        self.cpp_info.names["cmake_find_package"] = "mqtt_cpp_iface"
        self.cpp_info.names["cmake_find_package_multi"] = "mqtt_cpp_iface"
