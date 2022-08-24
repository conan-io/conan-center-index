import os
import glob
from from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.29.1"

class MosquittoConan(ConanFile):
    name = "mosquitto"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/mosquitto"
    topics = ("mqtt", "broker", "libwebsockets", "mosquitto", "eclipse", "iot")
    license = "EPL-1.0", "BSD-3-Clause" # https://lists.spdx.org/g/Spdx-legal/message/2701
    description = "Eclipse Mosquitto - An open source MQTT broker"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_tls": [True, False],
               "with_websockets": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_tls": True,
                       "with_websockets": True}
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_tls:
            self.requires("openssl/1.1.1i")
        if self.options.with_websockets:
            self.requires("libwebsockets/4.1.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["WITH_PIC"] = self.options.get_safe("fPIC", True)
            self._cmake.definitions["WITH_STATIC_LIBRARIES"] = not self.options.shared
            self._cmake.definitions["WITH_TLS"] = self.options.with_tls
            self._cmake.definitions["WITH_TLS_PSK"] = self.options.with_tls
            self._cmake.definitions["WITH_EC"] = self.options.with_tls
            self._cmake.definitions["DOCUMENTATION"] = False
            self._cmake.definitions["WITH_THREADING"] = self.settings.compiler != "Visual Studio"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        if self.settings.os == "Windows":
            if self.options.with_tls:
                tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"),
                                    "set (LIBRARIES ${LIBRARIES} ws2_32)",
                                    "set (LIBRARIES ${LIBRARIES} ws2_32 crypt32)")
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                                    "set (MOSQ_LIBS ${MOSQ_LIBS} ws2_32)",
                                    "set (MOSQ_LIBS ${MOSQ_LIBS} ws2_32 crypt32)")
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                                    "target_link_libraries(mosquitto_passwd ${OPENSSL_LIBRARIES})",
                                    "target_link_libraries(mosquitto_passwd ${OPENSSL_LIBRARIES} ws2_32 crypt32)")
            tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"),
                                "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                                "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")
            tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "cpp", "CMakeLists.txt"),
                                "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                                "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="edl-v10", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="epl-v10", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="mosquitto.conf", src=self._source_subfolder, dst="res")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "etc"))
        if not self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dll*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dylib")

    def package_info(self):
        lib_suffix = "_static" if not self.options.shared else ""
        # FIXME: there should be no namespace for CMake targets
        self.cpp_info.components["libmosquitto"].name = "mosquitto"
        self.cpp_info.components["libmosquitto"].libs = ["mosquitto" + lib_suffix]
        self.cpp_info.components["libmosquitto"].names["pkgconfig"] = "libmosquitto"
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
        elif self.settings.os == "Linux":
            self.cpp_info.components["libmosquitto"].system_libs.extend(["rt", "pthread", "dl"])

        self.cpp_info.components["libmosquittopp"].name = "mosquittopp"
        self.cpp_info.components["libmosquittopp"].libs = ["mosquittopp" + lib_suffix]
        self.cpp_info.components["libmosquittopp"].requires = ["libmosquitto"]
        self.cpp_info.components["libmosquittopp"].names["pkgconfig"] = "libmosquittopp"
        if not self.options.shared:
            self.cpp_info.components["libmosquitto"].defines.append("LIBMOSQUITTO_STATIC")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
