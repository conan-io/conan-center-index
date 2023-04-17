from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, replace_in_file
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class PahoMqttcConan(ConanFile):
    name = "paho-mqtt-c"
    description = "Eclipse Paho MQTT C client library for Linux, Windows and MacOS"
    license = "EPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/paho.mqtt.c"
    topics = ("mqtt", "iot", "eclipse", "ssl", "tls", "paho")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
        "asynchronous": [True, False],
        "high_performance": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": True,
        "asynchronous": True,
        "high_performance": False,
    }

    @property
    def _has_high_performance_option(self):
        return Version(self.version) >= "1.3.2"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not self._has_high_performance_option:
            del self.options.high_performance

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.ssl:
            # Headers are exposed https://github.com/eclipse/paho.mqtt.c/blob/f7799da95e347bbc930b201b52a1173ebbad45a7/src/SSLSocket.h#L29
            self.requires("openssl/1.1.1t", transitive_headers=True)

    def validate(self):
        if not self.options.shared and Version(self.version) < "1.3.4":
            raise ConanInvalidConfiguration(f"{self.ref} does not support static linking")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PAHO_ENABLE_TESTING"] = False
        tc.variables["PAHO_BUILD_DOCUMENTATION"] = False
        tc.variables["PAHO_ENABLE_CPACK"] = False
        tc.variables["PAHO_BUILD_DEB_PACKAGE"] = False
        tc.variables["PAHO_BUILD_ASYNC"] = self.options.asynchronous
        tc.variables["PAHO_BUILD_STATIC"] = not self.options.shared
        tc.variables["PAHO_BUILD_SHARED"] = self.options.shared
        tc.variables["PAHO_BUILD_SAMPLES"] = False
        tc.variables["PAHO_WITH_SSL"] = self.options.ssl
        if self.options.ssl:
            tc.cache_variables["OPENSSL_SEARCH_PATH"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
            tc.cache_variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        if self._has_high_performance_option:
            tc.variables["PAHO_HIGH_PERFORMANCE"] = self.options.high_performance
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_source(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "SET(CMAKE_MODULE_PATH \"${CMAKE_SOURCE_DIR}/cmake/modules\")",
                        "LIST(APPEND CMAKE_MODULE_PATH \"${CMAKE_SOURCE_DIR}/cmake/modules\")")
        if not self.options.get_safe("fPIC", True):
            replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "POSITION_INDEPENDENT_CODE ON", "")

    def build(self):
        self._patch_source()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=self._cmake_target)

    def package(self):
        copy(self, "edl-v10", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, self._epl_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "notice.html", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        # Manually copy since the CMake installs everything
        copy(self, pattern="MQTT*.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))

        for suffix in ["lib", "a", "dylib"]:
            copy(self, pattern=f"*.{suffix}", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern=f"*{self._lib_target}.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern=f"*{self._lib_target}.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rm(self, "*.cmake", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.components["_paho-mqtt-c"].libs = [self._lib_target]

        self.cpp_info.set_property("cmake_file_name", "eclipse-paho-mqtt-c")

        self.cpp_info.components["_paho-mqtt-c"].set_property("cmake_target_name", f"eclipse-paho-mqtt-c::{self._cmake_target}")

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

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "eclipse-paho-mqtt-c"
        self.cpp_info.names["cmake_find_package_multi"] = "eclipse-paho-mqtt-c"
        self.cpp_info.components["_paho-mqtt-c"].names["cmake_find_package"] = self._cmake_target
        self.cpp_info.components["_paho-mqtt-c"].names["cmake_find_package_multi"] = self._cmake_target

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
            if Version(self.version) < "1.3.2" or self.settings.os == "Windows":
                target += "-static"
        return target
