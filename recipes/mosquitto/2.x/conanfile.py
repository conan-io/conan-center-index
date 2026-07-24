import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version


required_conan_version = ">=1.53.0"


class Mosquitto(ConanFile):
    name = "mosquitto"
    description = """Eclipse Mosquitto MQTT library, broker and more"""
    license = "EPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mosquitto.org"
    topics = ("MQTT", "IoT", "eclipse")
    package_type = "library"
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

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # mosquitto 2.1 requires cJSON unconditionally (libmosquitto_common),
        # so only tie cjson to clients for older versions.
        if not self.options.clients and Version(self.version) < "2.1":
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
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("cjson") or Version(self.version) >= "2.1":
            self.requires("cjson/1.7.16")
        if self.options.get_safe("websockets"):
            self.requires("libwebsockets/4.3.2")
        if self.options.get_safe("threading") and self.settings.os == "Windows" and Version(self.version) >= "2.0.21":
            self.requires("pthreads4w/3.0.0")

    def build_requirements(self):
        # cmake_minimum_version is 3.18 in CMakeLists.txt for mosquitto >= 2.0.21
        self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        if self.options.get_safe("threading") and self.settings.os == "Windows" and Version(self.version) >= "2.0.21":
            deps.set_property("pthreads4w", "cmake_target_aliases", ["PThreads4W::PThreads4W"])
        if Version(self.version) >= "2.1":
            # mosquitto 2.1 links a bare `cJSON` target (see libcommon/CMakeLists.txt),
            # which is normally provided by its bundled cmake/FindcJSON.cmake. Alias
            # Conan's cjson target to that name so the include dirs propagate when the
            # Conan config package is used instead of the module finder.
            deps.set_property("cjson", "cmake_target_aliases", ["cJSON"])
        deps.generate()

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
        if self.settings.os == "Windows" and Version(self.version) < "2.0.21":
            # Threading not supported by recipe before 2.0.21
            tc.variables["WITH_THREADING"] = False
        else:
            tc.variables["WITH_THREADING"] = self.options.threading
        tc.variables["WITH_WEBSOCKETS"] = self.options.get_safe("websockets", False)
        tc.variables["STATIC_WEBSOCKETS"] = self.options.get_safe("websockets", False) and not self.dependencies["libwebsockets"].options.shared
        tc.variables["WITH_DOCS"] = False
        tc.variables["WITH_TESTS"] = False
        tc.variables["CMAKE_INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "res").replace("\\", "/")
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if Version(self.version) >= "2.1":
            # mosquitto 2.1's static library target (libmosquitto_static) omits the
            # bundled-deps include dir that only the shared target adds via
            # `if(WITH_BUNDLED_DEPS)` in lib/CMakeLists.txt. As a result headers like
            # utlist.h/uthash.h from deps/ aren't found when building the static lib.
            # Add the include dir explicitly for all targets.
            deps_dir = os.path.join(self.source_folder, "deps").replace("\\", "/")
            tc.extra_cflags.append(f"-I{deps_dir}")
            tc.extra_cxxflags.append(f"-I{deps_dir}")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE.txt", "edl-v10", "epl-v20"):
            copy(self, license_file, self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.example", os.path.join(self.package_folder, "res"))
        package_lib_folder = os.path.join(self.package_folder, "lib")
        if not self.options.shared:
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "mosquitto.lib", package_lib_folder)
            rm(self, "mosquittopp.lib", package_lib_folder)
            rm(self, "*.dll.a", package_lib_folder)
            rm(self, "*.so*", package_lib_folder)
            rm(self, "*.dylib", package_lib_folder)
        elif self.options.shared and is_msvc(self):
            lib_folder = os.path.join(self.build_folder, "lib", str(self.settings.build_type))
            copy(self, "mosquitto.lib", lib_folder, package_lib_folder)
            if self.options.build_cpp:
                libpp_folder = os.path.join(self.build_folder, "lib", "cpp", str(self.settings.build_type))
                copy(self, "mosquittopp.lib", libpp_folder, package_lib_folder)

    def package_info(self):
        lib_suffix = "" if self.options.shared else "_static"
        self.cpp_info.components["libmosquitto"].set_property("pkg_config_name", "libmosquitto")
        self.cpp_info.components["libmosquitto"].libs = [f"mosquitto{lib_suffix}"]
        self.cpp_info.components["libmosquitto"].resdirs = ["res"]
        if not self.options.shared:
            self.cpp_info.components["libmosquitto"].defines = ["LIBMOSQUITTO_STATIC"]
        if self.options.ssl:
            self.cpp_info.components["libmosquitto"].requires = ["openssl::openssl"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libmosquitto"].system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libmosquitto"].system_libs = ["ws2_32"]
            if self.options.get_safe("threading") and Version(self.version) >= "2.0.21":        
                self.cpp_info.components["libmosquitto"].requires.append("pthreads4w::pthreads4w")

        if self.options.build_cpp:
            self.cpp_info.components["libmosquittopp"].set_property("pkg_config_name", "libmosquittopp")
            self.cpp_info.components["libmosquittopp"].libs = [f"mosquittopp{lib_suffix}"]
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
