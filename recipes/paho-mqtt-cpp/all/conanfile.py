from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, rmdir, get
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

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
        "ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": True
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

        self.options["paho-mqtt-c/*"].shared = self.options.shared
        self.options["paho-mqtt-c/*"].ssl = self.options.ssl

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if self.dependencies["paho-mqtt-c"].options.shared != self.options.shared:
            raise ConanInvalidConfiguration(f"{self.name} requires paho-mqtt-c to have a matching 'shared' option.")
        if self.dependencies["paho-mqtt-c"].options.ssl != self.options.ssl:
            raise ConanInvalidConfiguration(f"{self.name} requires paho-mqtt-c to have a matching 'ssl' option.")
        if Version(self.version) < "1.2.0" and Version(self.dependencies["paho-mqtt-c"].ref.version) >= "1.3.2":
            raise ConanInvalidConfiguration(f"{self.name}/{self.version} requires paho-mqtt-c =< 1.3.1")

    def requirements(self):
        if Version(self.version) >= "1.2.0":
            self.requires("paho-mqtt-c/1.3.9", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("paho-mqtt-c/1.3.1", transitive_headers=True, transitive_libs=True) # https://github.com/eclipse/paho.mqtt.cpp/releases/tag/v1.1
        # upstream's cmakefiles reference openssl directly with ssl enabled, so we
        # should directly depend, not just transitively.
        if self.options.ssl:
            self.requires("openssl/1.1.1t")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PAHO_BUILD_DOCUMENTATION"] = False
        tc.variables["PAHO_BUILD_SAMPLES"] = False
        tc.variables["PAHO_BUILD_STATIC"] = not self.options.shared
        tc.variables["PAHO_BUILD_SHARED"] = self.options.shared
        tc.variables["PAHO_WITH_SSL"] = self.options.ssl
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        vbuildenv = VirtualBuildEnv(self)
        vbuildenv.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
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
        self.cpp_info.names["cmake_find_package"] = "PahoMqttCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "PahoMqttCpp"
        self.cpp_info.set_property("cmake_file_name", "PahoMqttCpp")

        target = "paho-mqttpp3" if self.options.shared else "paho-mqttpp3-static"
        self.cpp_info.components["paho-mqttpp"].set_property("cmake_target_name", f"PahoMqttCpp::{target}")
        self.cpp_info.components["paho-mqttpp"].names["cmake_find_package"] = target
        self.cpp_info.components["paho-mqttpp"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["paho-mqttpp"].requires = ["paho-mqtt-c::paho-mqtt-c"]
        if self.settings.os == "Windows":
            self.cpp_info.components["paho-mqttpp"].libs = [target]
        else:
            self.cpp_info.components["paho-mqttpp"].libs = ["paho-mqttpp3"]
