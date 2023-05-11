import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version


required_conan_version = ">=1.53.0"


class Mosquitto(ConanFile):
    name = "mosquitto"
    license = "EPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mosquitto.org"
    description = """Eclipse Mosquitto MQTT library, broker and more"""
    topics = ("MQTT", "IoT", "eclipse")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
        "clients": [True, False],
        "broker": [True, False],
        "apps": [True, False],
        "cjson": [True, False],
        "build_cpp": [True, False],
        "websockets": [True, False],
        "threading": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": True,
        "clients": False,
        "broker": False,
        "apps": False,
        "cjson": True, # https://github.com/eclipse/mosquitto/commit/bbe0afbfbe7bb392361de41e275759ee4ef06b1c
        "build_cpp": True,
        "websockets": False,
        "threading": True,
    }
    generators = "CMakeDeps"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.clients:
            self.options.rm_safe("cjson")
        if not self.options.broker:
            self.options.rm_safe("websockets")
        if not self.options.build_cpp:
            self.options.rm_safe("compiler.libcxx")
            self.options.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1q")
        if self.options.get_safe("cjson"):
            self.requires("cjson/1.7.14")
        if self.options.get_safe("websockets"):
            self.requires("libwebsockets/4.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_STATIC_LIBRARIES"] = not self.options.shared
        tc.variables["WITH_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["WITH_TLS"] = self.options.ssl
        tc.variables["WITH_CLIENTS"] = self.options.clients
        if Version(self.version) < "2.0.6":
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_cJSON"] = not self.options.get_safe("cjson")
        else:
            tc.variables["WITH_CJSON"] = self.options.get_safe("cjson")
        tc.variables["WITH_BROKER"] = self.options.broker
        tc.variables["WITH_APPS"] = self.options.apps
        tc.variables["WITH_PLUGINS"] = False
        tc.variables["WITH_LIB_CPP"] = self.options.build_cpp
        tc.variables["WITH_THREADING"] = not is_msvc(self) and self.options.threading
        tc.variables["WITH_WEBSOCKETS"] = self.options.get_safe("websockets", False)
        tc.variables["STATIC_WEBSOCKETS"] = self.options.get_safe("websockets", False) and not self.options["libwebsockets"].shared
        tc.variables["DOCUMENTATION"] = False
        tc.variables["CMAKE_INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "res").replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE.txt", "edl-v10", "epl-v20"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.example", os.path.join(self.package_folder, "res"))
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
        elif self.options.shared and self.settings.compiler == "Visual Studio":
            copy(self, "mosquitto.lib", src=os.path.join(self.build_folder, "lib"), dst="lib")
            if self.options.build_cpp:
                copy(self, "mosquittopp.lib", src=os.path.join(self.build_folder, "lib"), dst="lib")

    def package_info(self):
        libsuffix = "" if self.options.shared else "_static"
        self.cpp_info.components["libmosquitto"].names["pkg_config"] = "libmosquitto"
        self.cpp_info.components["libmosquitto"].libs = ["mosquitto" + libsuffix]
        if self.options.ssl:
            self.cpp_info.components["libmosquitto"].requires = ["openssl::openssl"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libmosquitto"].system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libmosquitto"].system_libs = ["ws2_32"]

        if self.options.build_cpp:
            self.cpp_info.components["libmosquittopp"].names["pkg_config"] = "libmosquittopp"
            self.cpp_info.components["libmosquittopp"].libs = ["mosquittopp" + libsuffix]
            self.cpp_info.components["libmosquittopp"].requires = ["libmosquitto"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libmosquittopp"].system_libs = ["pthread", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["libmosquittopp"].system_libs = ["ws2_32"]

        if self.options.broker:
            self.cpp_info.components["mosquitto_broker"].libdirs = []
            self.cpp_info.components["mosquitto_broker"].includedirs = []
            if self.options.websockets:
                self.cpp_info.components["mosquitto_broker"].requires.append("libwebsockets::libwebsockets")
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.components["mosquitto_broker"].system_libs = ["pthread", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["mosquitto_broker"].system_libs = ["ws2_32"]

        for option in ["apps", "clients"]:
            if self.options.get_safe(option):
                option_comp_name = "mosquitto_{}".format(option)
                self.cpp_info.components[option_comp_name].libdirs = []
                self.cpp_info.components[option_comp_name].includedirs = []
                self.cpp_info.components[option_comp_name].requires = ["openssl::openssl", "libmosquitto"]
                if self.options.cjson:
                    self.cpp_info.components[option_comp_name].requires.append("cjson::cjson")

        # TODO: to remove in conan v2
        if self.options.broker or self.options.get_safe("apps") or self.options.get_safe("clients"):
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
