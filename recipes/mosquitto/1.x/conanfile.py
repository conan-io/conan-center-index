from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class MosquittoConan(ConanFile):
    name = "mosquitto"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/mosquitto"
    topics = ("mqtt", "broker", "libwebsockets", "eclipse", "iot")
    license = "EPL-1.0", "BSD-3-Clause" # https://lists.spdx.org/g/Spdx-legal/message/2701
    description = "Eclipse Mosquitto - An open source MQTT broker"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tls": [True, False],
        "with_websockets": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tls": True,
        "with_websockets": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tls:
            self.requires("openssl/1.1.1s")
        if self.options.with_websockets:
            self.requires("libwebsockets/4.3.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["WITH_STATIC_LIBRARIES"] = not self.options.shared
        tc.variables["WITH_TLS"] = self.options.with_tls
        tc.variables["WITH_TLS_PSK"] = self.options.with_tls
        tc.variables["WITH_EC"] = self.options.with_tls
        tc.variables["DOCUMENTATION"] = False
        tc.variables["WITH_THREADING"] = not is_msvc(self)
        tc.variables["CMAKE_INSTALL_SYSCONFDIR"] = "res"
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE.txt", "edl-v10", "epl-v10"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if not self.options.shared:
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "mosquitto.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "mosquittopp.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll.a", os.path.join(self.package_folder, "lib"))
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        lib_suffix = "_static" if not self.options.shared else ""
        self.cpp_info.components["libmosquitto"].set_property("pkg_config_name", "libmosquitto")
        self.cpp_info.components["libmosquitto"].libs = [f"mosquitto{lib_suffix}"]
        self.cpp_info.components["libmosquitto"].resdirs = ["res"]
        if not self.options.shared:
            self.cpp_info.components["libmosquitto"].defines.append("LIBMOSQUITTO_STATIC")
        if self.options.with_tls:
            self.cpp_info.components["libmosquitto"].requires.append("openssl::openssl")
            self.cpp_info.components["libmosquitto"].defines.extend(["WITH_TLS", "WITH_TLS_PSK", "WITH_EC"])
        if self.options.with_websockets:
            self.cpp_info.components["libmosquitto"].requires.append("libwebsockets::libwebsockets")
            self.cpp_info.components["libmosquitto"].defines.append("WITH_WEBSOCKETS")
        if self.settings.os == "Windows":
            self.cpp_info.components["libmosquitto"].system_libs.append("ws2_32")
            if self.options.with_tls:
                self.cpp_info.components["libmosquitto"].system_libs.append("crypt32")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libmosquitto"].system_libs.extend(["rt", "pthread", "dl"])

        self.cpp_info.components["libmosquittopp"].set_property("pkg_config_name", "libmosquittopp")
        self.cpp_info.components["libmosquittopp"].libs = [f"mosquittopp{lib_suffix}"]
        self.cpp_info.components["libmosquittopp"].requires = ["libmosquitto"]

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
