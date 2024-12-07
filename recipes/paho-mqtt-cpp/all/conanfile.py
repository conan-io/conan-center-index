from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, rmdir, get
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


class PahoMqttCppConan(ConanFile):
    name = "paho-mqtt-cpp"
    description = "The open-source client implementations of MQTT and MQTT-SN"
    license = "EPL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.cpp"
    topics = ("mqtt", "iot", "eclipse", "ssl", "paho", "cpp")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        suffix = "" if Version(conan_version).major < "2" else "/*"
        self.options[f"paho-mqtt-c{suffix}"].shared = self.options.shared

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Headers are exposed https://github.com/conan-io/conan-center-index/pull/16760#issuecomment-1502420549
        # Symbols are exposed   "_MQTTProperties_free", referenced from: mqtt::connect_options::~connect_options() in test_package.cpp.o
        self.requires("paho-mqtt-c/1.3.13", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if self.dependencies["paho-mqtt-c"].options.shared != self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} requires paho-mqtt-c to have a matching 'shared' option.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PAHO_BUILD_DOCUMENTATION"] = False
        tc.variables["PAHO_BUILD_SAMPLES"] = False
        tc.variables["PAHO_BUILD_STATIC"] = not self.options.shared
        tc.variables["PAHO_BUILD_SHARED"] = self.options.shared
        tc.variables["PAHO_WITH_SSL"] = self.dependencies["paho-mqtt-c"].options.ssl
        tc.generate()
        deps = CMakeDeps(self)
        if Version(self.version) < "1.4.0":
            deps.set_property("paho-mqtt-c", "cmake_file_name", "PahoMqttC")
            deps.set_property("paho-mqtt-c", "cmake_target_name", "PahoMqttC::PahoMqttC")
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "edl-v10", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "epl-v10", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "notice.html", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        target = "paho-mqttpp3" if self.options.shared else "paho-mqttpp3-static"
        self.cpp_info.set_property("cmake_file_name", "PahoMqttCpp")
        self.cpp_info.set_property("cmake_target_name", f"PahoMqttCpp::{target}")
        # TODO: back to root level once conan v1 support removed
        if self.settings.os == "Windows":
            self.cpp_info.components["paho-mqttpp"].libs = [target]
        else:
            self.cpp_info.components["paho-mqttpp"].libs = ["paho-mqttpp3"]

        # TODO: to remove once conan v1 support removed
        self.cpp_info.names["cmake_find_package"] = "PahoMqttCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "PahoMqttCpp"
        self.cpp_info.components["paho-mqttpp"].names["cmake_find_package"] = target
        self.cpp_info.components["paho-mqttpp"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["paho-mqttpp"].set_property("cmake_target_name", f"PahoMqttCpp::{target}")
        self.cpp_info.components["paho-mqttpp"].requires = ["paho-mqtt-c::paho-mqtt-c"]
