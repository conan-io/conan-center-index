import os
from conan import ConanFile
from conan.tools.files import copy, get, replace_in_file, rmdir, rm
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout


required_conan_version = ">=1.47.0"


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
    exports_sources = ["CMakeLists.txt"]
    _cmake_toolchain = None

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.clients:
            del self.options.cjson
        if not self.options.broker:
            del self.options.websockets
        if not self.options.build_cpp:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

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

    def _configure_cmake_toolchain(self):
        if self._cmake_toolchain:
            return self._cmake_toolchain
        self._cmake_toolchain = CMakeToolchain(self)
        self._cmake_toolchain.variables["WITH_STATIC_LIBRARIES"] = not self.options.shared
        self._cmake_toolchain.variables["WITH_PIC"] = self.options.get_safe("fPIC", False)
        self._cmake_toolchain.variables["WITH_TLS"] = self.options.ssl
        self._cmake_toolchain.variables["WITH_CLIENTS"] = self.options.clients
        if Version(self.version) < "2.0.6":
            self._cmake_toolchain.variables["CMAKE_DISABLE_FIND_PACKAGE_cJSON"] = not self.options.get_safe("cjson")
        else:
            self._cmake_toolchain.variables["WITH_CJSON"] = self.options.get_safe("cjson")
        self._cmake_toolchain.variables["WITH_BROKER"] = self.options.broker
        self._cmake_toolchain.variables["WITH_APPS"] = self.options.apps
        self._cmake_toolchain.variables["WITH_PLUGINS"] = False
        self._cmake_toolchain.variables["WITH_LIB_CPP"] = self.options.build_cpp
        self._cmake_toolchain.variables["WITH_THREADING"] = self.settings.compiler != "msvc" and self.options.threading
        self._cmake_toolchain.variables["WITH_WEBSOCKETS"] = self.options.get_safe("websockets", False)
        self._cmake_toolchain.variables["STATIC_WEBSOCKETS"] = self.options.get_safe("websockets", False) and not self.options["libwebsockets"].shared
        self._cmake_toolchain.variables["DOCUMENTATION"] = False
        self._cmake_toolchain.variables["CMAKE_INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "res").replace("\\", "/")
        self._cmake_toolchain.generate()
        return self._cmake_toolchain

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "client", "CMakeLists.txt"), "static)", "static ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "client", "CMakeLists.txt"), "quitto)", "quitto ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "static)", "static ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "quitto)", "quitto ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_passwd", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "lib", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "MOSQ_LIBS", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "include", "mosquitto.h"), "__declspec(dllimport)", "")
        replace_in_file(self, os.path.join(self.source_folder, "lib", "cpp", "mosquittopp.h"), "__declspec(dllimport)", "")
        # dynlibs for apple mobile want code signatures and that will not work here
        # this would actually be the right patch for static builds also, but this would have other side effects, so
        if(self.settings.os in ["iOS", "watchOS", "tvOS"]):
            replace_in_file(self, os.path.join(self.source_folder, "lib", "CMakeLists.txt"), "SHARED", "")
            replace_in_file(self, os.path.join(self.source_folder, "lib", "cpp", "CMakeLists.txt"), "SHARED", "")

    def generate(self):
        self._configure_cmake_toolchain()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "edl-v10", src=self.source_folder, dst="licenses")
        copy(self, "epl-v20", src=self.source_folder, dst="licenses")
        copy(self, "LICENSE.txt", src=self.source_folder, dst="licenses")
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.example", os.path.join(self.package_folder, "res"))
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
        elif self.options.shared and self.settings.compiler == "Visual Studio":
            copy(self, "mosquitto.lib", src=os.path.join(self._build_subfolder, "lib"), dst="lib")
            if self.options.build_cpp:
                copy(self, "mosquittopp.lib", src=os.path.join(self._build_subfolder, "lib"), dst="lib")

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

        if self.options.broker or self.options.get_safe("apps") or self.options.get_safe("clients"):
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        if self.options.broker:
            self.cpp_info.components["mosquitto_broker"].libdirs = []
            self.cpp_info.components["mosquitto_broker"].include_dirs = []
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
                self.cpp_info.components[option_comp_name].include_dirs = []
                self.cpp_info.components[option_comp_name].requires = ["openssl::openssl", "libmosquitto"]
                if self.options.cjson:
                    self.cpp_info.components[option_comp_name].requires.append("cjson::cjson")
